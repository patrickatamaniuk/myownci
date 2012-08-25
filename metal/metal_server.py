#!/usr/bin/env python
#
# requirements:
# sudo pip install pika simplejson simpleyaml
#
import sys, time, atexit
import pika
import simplejson
import logging
from logging import debug
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
        self.state = 'unconfigured'
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
        self.state = 'ready'
        self.connection.add_timeout(2, self.announce_self)

    def tick(self):
        mlog(" [%s] tick" % (self.logkey,))
        self.announce_self()

    def on_request(self, ch, method, props, body):
        mlog(" [%s] Got request %r:%r" % (self.logkey, method.routing_key, body,))
        #announcements from a worker
        if method.routing_key in ('worker_alive.metal',
            'worker_ping_reply.metal',
            'worker_request_uuid.metal'):
            self.check_worker(body)
        #request from hub
        elif 'ping.metal' == method.routing_key:
            self.ping_reply()
        else:
            mlog(" [%s] Unknown request %r" % (self.logkey, method.routing_key))

    def announce_self(self):
        self.get_worker_status()
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
            'platform': self.config['var']['identity']['platform'],
            'state': self.state
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

#FIXME: implement vmadapter.find_by_uuid and vmadapter.find_by_hwaddr
#FIXME seed found_workers with defined workers so hub gets them even they did not announce themselves yet
        for configured_worker in self.config['workers']:
            debug('Check %r'% configured_worker)
            name = configured_worker['name']
#        for name, worker in self.config['var']['vmhostdefinitions'].items():
            if not name in self.config['var']['vmhostdefinitions']:
                mlog(" [%s] Configuration error: %s is not a defined guest" %(self.logkey, name))
                continue
            worker =  self.config['var']['vmhostdefinitions'][name]

            for hwaddr in workeraddrlist:
                if hwaddr in worker['hwaddr']:
                    mlog(" [%s] FOUND %s" %(self.logkey, name))
                    try:
                        found_workers = self.config['var']['found_workers']
                    except KeyError:
                        found_workers = {}
                    guest_uuid = None
                    try:
                        found_workers[name] = body['worker']
                        guest_uuid = body['envelope']['host-uuid']
                        del found_workers[name]['hwaddrlist']
                    except KeyError:
                        pass
                    if not guest_uuid:
#need to inform worker of its uuid
                        guest = self.vmadapter.guests[name]
                        found_workers[name]['host-uuid'] = guest['uuid']
                        mlog(" [%s] remembering guest uuid: %s" % (self.logkey, repr(guest['uuid'])))
                        self.update_guest_config(hwaddr, found_workers[name])
#FIXME found_workers is transported to hub. change name to something like 'workers'
                    self.config_object.set_var({'found_workers': found_workers})
                    self.config_object.save()
                    break

    def update_guest_config(self, hwaddr, worker):
        debug("Update guest config %r %r"% (worker, hwaddr+'.update_config.worker'))
        self.send(simplejson.dumps(worker),
                  exchange_name = self.exchange_name,
                  #routing_key = hwaddr+'.update_config.worker',
                  routing_key = 'update_config.%s'%hwaddr,
                  props = { 'content_type': 'application/json' })

    def shutdown(self):
        mlog(" [%s] exiting"% (self.logkey,))

    def get_worker_status(self):
        config.set_var({'vmhostdefinitions': self.vmadapter.ls()})
        #debug( self.config)
        for worker in self.config['workers']:
            debug('Update %r' %(worker))
            name = worker['name']
            if not worker['name'] in self.vmadapter.guests:
                continue
            debug(self.config['var']['vmhostdefinitions'][name])
            #debug('KNOWN found worker?:%r' % (self.config['var']['found_workers']))

        return
 
server = None
def cleanup():
    global server
    server.shutdown()

if __name__ == '__main__':
  logging.basicConfig(level=logging.DEBUG)
  config = Config('metal.yaml')
  server = AmqpMetalServer(config)
  atexit.register(cleanup)
