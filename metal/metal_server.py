#!/usr/bin/env python
#
# requirements:
# sudo pip install pika simplejson simpleyaml
#
import sys, time
import pika
import simplejson
from myownci import mlog
from myownci.Config import Config
from myownci.Identity import Identity
from myownci.Amqp import AmqpBase
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
        mlog(" [%s] Loaded config:\n"% (self.logkey,) , simplejson.dumps(config.config, indent=4, sort_keys=True))
        AmqpBase.__init__(self, config)

    def on_request(self, ch, method, props, body):
        mlog(" [%s] Got request %r:%r" % (self.logkey, method.routing_key, body,))
        if 'announce_worker.metal' == method.routing_key:
            self.check_worker(body)
        elif 'discover.metal' == method.routing_key:
            if 'get config' == body:
                self.reply(simplejson.dumps(self.config), ch, props)

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
                    print self.config
                    break
        print self.config['workers']
if __name__ == '__main__':
  config = Config('metal.yaml')
  AmqpMetalServer(config)
