#!/usr/bin/env python
#
# requirements:
# sudo pip install pika simplejson simpleyaml
#
import sys, time, atexit
import pika
import simplejson
from myownci import mlog
from myownci.Config import Config
from myownci.Identity import Identity
from myownci.Amqp import AmqpBase
from myownci.IntervalScheduler import IntervalScheduler
import vmadapter

class AmqpMetalServer(AmqpBase):
    routing_key = '*.metal'
    logkey = 'metal'
    def __init__(self, config):
        config.set_var({'identity' : Identity().id})
        config.save()

        self.vmadapter = vmadapter.VmKVM()
        config.set_var({'vmhostdefinitions': self.vmadapter.ls()})
        config.save()
        #mlog(" [%s] Loaded config:\n"% (self.logkey,) , simplejson.dumps(config.config, indent=4, sort_keys=True))
        AmqpBase.__init__(self, config)

    def on_connected(self, connection):
        self.heartbeat = IntervalScheduler(connection, callback=self.tick, interval=60)
        AmqpBase.on_connected(self, connection)

    def on_ready(self):
        self.connection.add_timeout(2, self.announce_self)

    def tick(self):
        mlog(" [%s] tick" % (self.logkey,))
        self.announce_self()

    def on_request(self, ch, method, props, body):
        mlog(" [%s] Got request %r:%r" % (self.logkey, method.routing_key, body,))
        #announcements from a worker
        if method.routing_key in ('worker_alive.metal', 'worker_ping_reply.metal'):
            self.check_worker(body)
        #request from hub
        elif 'ping.metal' == method.routing_key:
            self.ping_reply()
        else:
            mlog(" [%s] Unknown request %r" % (self.logkey, method.routing_key))

    def announce_self(self):
        self.ping_reply(routing_key='metal_alive.hub') #reuse

    def ping_reply(self, routing_key='metal_ping_reply.hub'):
        data = {}
        data['envelope'] = {
            'host-uuid': self.config['host-uuid'],
            'hostname': self.config['hostname']
        }
        try:
            data['workers'] = [w for w in self.config['var']['found_workers'].values()]
        except KeyError:
            data['workers'] = []
        data['metal'] = {
            'platform': self.config['var']['identity']['platform']
        }
        self.send(simplejson.dumps(data),
                  exchange_name = self.exchange_name,
                  routing_key = routing_key,
                  props = { 'content_type': 'application/json' })
        #mlog(" [%s] Sent %r:%r" % (self.logkey, routing_key, repr(data)))
        mlog(" [%s] Sent %r" % (self.logkey, routing_key))

    def check_worker(self, body):
        try:
            body = simplejson.loads(body)
        except simplejson.decoder.JSONDecodeError:
            mlog(" [%s] invalid request from worker" % (self.logkey, ))
            return
        try:
            workeraddrlist = body['worker']['hwaddrlist']
        except KeyError:
            mlog(" [%s] invalid request from worker" % (self.logkey, ))
            return
        mlog(" [%s] check worker %s" % (self.logkey, repr(workeraddrlist)))

        for name, worker in self.config['var']['vmhostdefinitions'].items():
            if not name in self.vmadapter.guests:
                mlog(" [%s] Configuration error: %s is not a defined guest" %(self.logkey, name))
                continue
            for hwaddr in workeraddrlist:
                if hwaddr in worker['hwaddr']:
                    mlog(" [%s] FOUND %s" %(self.logkey, name))
                    try:
                        found_workers = self.config['var']['found_workers']
                    except KeyError:
                        found_workers = {}
                    try:
                        found_workers[name] = body['worker']
                        found_workers[name]['host-uuid'] = body['envelope']['host-uuid']
                        del found_workers[name]['hwaddrlist']
                    except KeyError:
                        pass
                    if not found_workers[name]['host-uuid']:
#need to inform worker of its uuid
                        guest = self.vmadapter.guests[name]
                        found_workers[name]['host-uuid'] = guest['uuid']
                        self.update_guest_config(hwaddr, found_workers[name])
                    self.config_object.set_var({'found_workers': found_workers})
                    self.config_object.save()
                    break

    def update_guest_config(self, hwaddr, worker):
        print "Update guest config", worker, hwaddr+'.update_config.worker'
        self.send(simplejson.dumps(worker),
                  exchange_name = self.exchange_name,
                  #routing_key = hwaddr+'.update_config.worker',
                  routing_key = 'update_config.%s'%hwaddr,
                  props = { 'content_type': 'application/json' })

    def shutdown(self):
        mlog(" [%s] exiting"% (self.logkey,))
 
server = None
def cleanup():
    global server
    server.shutdown()

if __name__ == '__main__':
  config = Config('metal.yaml')
  server = AmqpMetalServer(config)
  atexit.register(cleanup)
