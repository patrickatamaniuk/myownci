#!/usr/bin/env python
import pika
import simplejson
from Config import Config
from Identity import Identity

class AmqpMetalServer:
    def __init__(self, config):
        self.config = config.config

        config.set_var({'identity' : Identity().id})
        config.save()
        print config.config
        self.connect()

    def connect(self):
        print(" [metal] Connecting to %s"% (self.config['amqp-server']['address'],))
        credentials = pika.PlainCredentials(self.config['amqp-server']['username'], self.config['amqp-server']['password'])
        self.connection = pika.SelectConnection(pika.ConnectionParameters(
                host=self.config['amqp-server']['address'],
                credentials = credentials),
                self.on_connected)
        try:
            self.connection.ioloop.start()
        except KeyboardInterrupt:
            self.connection.close()
            self.connection.ioloop.start()

    def on_connected(self, connection):
        print(" [metal] Connected to RabbitMQ")
        connection.channel(self.on_channel_open)

    def on_channel_open(self, channel_):
        self.channel = channel_
        print(" [metal] Received our Channel")

        self.channel.exchange_declare(exchange='myownci_discover',
                                 type='topic',
                                 callback=self.on_exchange_declared)

    def on_exchange_declared(self, frame):
        print(" [metal] Excange declared")
        self.channel.queue_declare(exclusive=True,
                                  callback=self.on_queue_declared)
    def on_queue_declared(self, frame):
        print(" [metal] Queue declared")
        self.queue = frame.method.queue
        self.channel.queue_bind(exchange='myownci_discover',
                           queue=self.queue,
                           routing_key = 'discover.metal',
                           callback = self.on_queue_bound)
    def on_queue_bound(self, frame):
        print " [metal] Awaiting RPC requests"
        self.channel.basic_consume(self.on_request,
                              queue=self.queue,
                              no_ack=True)

    def on_request(self, ch, method, props, body):
        print repr(body)
        print " [metal] Got request %r:%r" % (method.routing_key, body,)
        if 'get config' == body:
            self.reply(simplejson.dumps(self.config), ch, props)

    def reply(self, response, ch, props):
        print " [metal] Sending reply"
        ch.basic_publish(exchange='',
                         routing_key=props.reply_to,
                         properties=pika.BasicProperties(correlation_id = \
                                                         props.correlation_id),
                         body=response)

if __name__ == '__main__':
  config = Config()
  AmqpMetalServer(config)
