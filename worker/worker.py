#!/usr/bin/env python
#
# installation:
# sudo apt-get install python-pip
# sudo pip install myownci_pysupport
# sudo pip install simpleyaml
# sudo pip install amqp

from myownci.Config import Config
from myownci.Identity import Identity
from myownci.Amqp import AmqpBase, AmqpListener

class Worker(AmqpBase):
    logkey = 'worker'
    def __init__(self, config):
        config.set_var({'identity' : Identity().id})
        print config.config
        config.save()
        AmqpBase.__init__(self, config)

    def on_channel_open(self, channel_):
        AmqpBase.on_channel_open(self, channel_)
        self.discover_listener = AmqpListener(self.channel,
            routing_key='discover.worker',
            request_callback=self.on_request_discover_worker)
        self.discover_listener.logkey = 'worker'
        self.discover_listener.exchange('myownci_discover')

    def on_request_discover_worker(self, ch, method, props, body):
        mlog(" [%s] Got request %r:%r" % (self.logkey, method.routing_key, body,))
        if 'get config' == body:
            self.reply(simplejson.dumps(self.config), ch, props)

def main():
    config = Config('worker.yaml')
    Worker(config)

if __name__ == '__main__':
  main()
