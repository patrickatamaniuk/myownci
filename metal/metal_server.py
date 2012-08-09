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
from myownci.Amqp import AmqpListener, AmqpBase
import vmadapter

class AmqpMetalServer(AmqpBase):
    discover_listener = None

    def __init__(self, config):
        config.set_var({'identity' : Identity().id})
        config.save()

        self.vmadapter = vmadapter.VmKVM()
        config.set_var({'vmhostdefinitions': self.vmadapter.ls()})
        config.save()
        mlog(config.config)
        print "Initialized."
        AmqpBase.__init__(self, config)

    def on_channel_open(self, channel_):
        AmqpBase.on_channel_open(self, channel_)
        self.discover_listener = AmqpListener(self.channel,
            routing_key='discover.metal',
            request_callback=self.on_request_discover_metal)
        self.discover_listener.exchange('myownci_discover')

    def on_request_discover_metal(self, ch, method, props, body):
        mlog(" [metal] Got request %r:%r" % (method.routing_key, body,))
        if 'get config' == body:
            self.reply(simplejson.dumps(self.config), ch, props)

if __name__ == '__main__':
  config = Config('metal.yaml')
  AmqpMetalServer(config)
