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
        mlog(" [%s] Connected to RabbitMQ" % (self.logkey,))
        self.heartbeat = IntervalScheduler(connection, callback=self.tick, interval=60)
        AmqpBase.on_connected(self, connection)

    def on_ready(self):
        self.connection.add_timeout(2, self.announce_self)

    def tick(self):
        mlog(" [%s] tick" % (self.logkey,))
        self.announce_self()

    def on_request(self, ch, method, props, body):
        mlog(" [%s] Got request %r:%r" % (self.logkey, method.routing_key, body,))
        if 'announce_worker.metal' == method.routing_key:
            self.check_worker(body)
        elif 'ping.metal' == method.routing_key:
            self.ping_reply()
        else:
            mlog(" [%s] Unknown request %r" % (self.logkey, method.routing_key))

    def announce_self(self):
        self.ping_reply(routing_key='metal_alive.hub') #reuse

    def ping_reply(self, routing_key='metal_ping_reply.hub'):
        data = self.config
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
            workeraddrlist = body['var']['identity']['hwaddrlist']
        except KeyError:
            mlog(" [%s] invalid request from worker" % (self.logkey, ))
            return
        mlog(" [%s] check worker %s" % (self.logkey, repr(workeraddrlist)))

        for name, worker in self.config['var']['vmhostdefinitions'].items():
            for hwaddr in workeraddrlist:
                if hwaddr in worker['hwaddr']:
                    print 'FOUND', name
                    try:
                        found_workers = self.config['var']['found_workers']
                    except KeyError:
                        found_workers = {}
                    found_workers[name] = body
                    self.config_object.set_var({'found_workers': found_workers})
                    self.config_object.save()
                    #print self.config
                    break
        #print self.config['workers']

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
