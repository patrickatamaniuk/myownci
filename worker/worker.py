#!/usr/bin/env python
#
# installation:
# sudo apt-get install python-pip
# sudo pip install myownci_pysupport
# sudo pip install simpleyaml
# sudo pip install pika
import simplejson

from myownci.Config import Config
from myownci.Identity import Identity
from myownci.Amqp import AmqpBase
from myownci import mlog

class Worker(AmqpBase):
    logkey = 'worker'
    routing_key = '*.worker'
    app_id = 'worker'

    def __init__(self, config):
        config.set_var({'identity' : Identity().id})
        config.save()
        AmqpBase.__init__(self, config)

    def on_queue_bound(self, frame):
        AmqpBase.on_queue_bound(self, frame)
        self.announce_self()

    def on_request(self, ch, method, props, body):
        mlog(" [%s] Got request %r:%r" % (self.logkey, method.routing_key, body,))
        if 'get config' == body:
            self.reply(simplejson.dumps(self.config), ch, props)

    def announce_self(self):
        routing_key = 'announce_worker.metal'
        data = {}
        data.update(self.config)
        del(data['amqp-server'])
        self.send(simplejson.dumps(data),
          exchange_name = self.exchange_name,
          routing_key = routing_key,
          props = { 'content_type': 'application/json' })
        mlog(" [%s] Sent %r:%r" % (self.logkey, routing_key, repr(data)))

def main():
    config = Config('worker.yaml')
    Worker(config)

if __name__ == '__main__':
  main()
