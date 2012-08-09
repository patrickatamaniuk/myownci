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

    def __init__(self, config):
        config.set_var({'identity' : Identity().id})
        config.save()

        self.vmadapter = vmadapter.VmKVM()
        config.set_var({'vmhostdefinitions': self.vmadapter.ls()})
        config.save()
        mlog(config.config)
        print "Initialized."
        AmqpBase.__init__(self, config)

    def on_request(self, ch, method, props, body):
        mlog(" [metal] Got request %r:%r" % (method.routing_key, body,))
        if 'get config' == body:
            self.reply(simplejson.dumps(self.config), ch, props)

if __name__ == '__main__':
  config = Config('metal.yaml')
  AmqpMetalServer(config)
