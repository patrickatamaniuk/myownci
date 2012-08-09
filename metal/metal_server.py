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
import vmadapter

class AmqpBase:
    def __init__(self, config):
        self.config = config.config
        self.connect(self.config['amqp-server']['address'],
                     self.config['amqp-server']['username'],
                     self.config['amqp-server']['password'])

    def connect(self, server, username, password):
        mlog(" [metal] Connecting to %s"% (server,) )
        credentials = pika.PlainCredentials(username, password)
        try:
            self.connection = pika.SelectConnection(pika.ConnectionParameters(
                host=server,
                credentials = credentials),
                self.on_connected)
        except Exception, e:
            mlog(" [metal] Connection error", e)
            time.sleep(60)
            sys.exit(3)
        try:
            self.connection.ioloop.start()
        except KeyboardInterrupt:
            self.connection.close()
            self.connection.ioloop.start()

    def on_connected(self, connection):
        mlog(" [metal] Connected to RabbitMQ")
        connection.channel(self.on_channel_open)

    def on_channel_open(self, channel_):
        self.channel = channel_
        mlog(" [metal] Received our Channel")

    def reply(self, response, ch, props):
        mlog(" [metal] Sending reply")
        ch.basic_publish(exchange='',
                         routing_key=props.reply_to,
                         properties=pika.BasicProperties(correlation_id = \
                                                         props.correlation_id),
                         body=response)

class AmqpListener:
    def __init__(self, channel, routing_key='', request_callback=None):
        self.channel = channel
        self.request_callback = request_callback
        self.routing_key = routing_key

    def exchange(self, name):
        self.exchange_name = name
        self.channel.exchange_declare(exchange=name,
                                 type='topic',
                                 callback=self.on_exchange_declared)
    def on_exchange_declared(self, frame):
        mlog(" [metal] Excange %s declared" %(self.exchange_name,))
        self.channel.queue_declare(exclusive=True,
                                  callback=self.on_queue_declared)

    def on_queue_declared(self, frame):
        mlog(" [metal] Queue declared")
        self.queue = frame.method.queue
        self.channel.queue_bind(exchange=self.exchange_name,
                           queue=self.queue,
                           routing_key = self.routing_key,
                           callback = self.on_queue_bound)
    def on_queue_bound(self, frame):
        mlog(" [metal] Awaiting RPC requests")
        self.channel.basic_consume(self.on_request,
                              queue=self.queue,
                              no_ack=True)

    def on_request(self, ch, method, props, body):
        if self.request_callback:
          self.request_callback(ch, method, props, body)


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
