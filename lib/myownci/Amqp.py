import sys, time
import pika
from myownci import mlog

class AmqpBase:
    logkey = 'metal'
    def __init__(self, config):
        self.config = config.config
        self.connect(self.config['amqp-server']['address'],
                     self.config['amqp-server']['username'],
                     self.config['amqp-server']['password'])

    def connect(self, server, username, password):
        mlog(" [%s] Connecting to %s"% (self.logkey, server,) )
        credentials = pika.PlainCredentials(username, password)
        try:
            self.connection = pika.SelectConnection(pika.ConnectionParameters(
                host=server,
                credentials = credentials),
                self.on_connected)
        except Exception, e:
            mlog(" [%s] Connection error" % (self.logkey, ), e)
            time.sleep(60)
            sys.exit(3)
        try:
            self.connection.ioloop.start()
        except KeyboardInterrupt:
            self.connection.close()
            self.connection.ioloop.start()

    def on_connected(self, connection):
        mlog(" [%s] Connected to RabbitMQ" % (self.logkey,))
        connection.channel(self.on_channel_open)

    def on_channel_open(self, channel_):
        self.channel = channel_
        mlog(" [%s] Received our Channel" % (self.logkey,))

    def reply(self, response, ch, props):
        mlog(" [%s] Sending reply" % (self.logkey, ))
        ch.basic_publish(exchange='',
                         routing_key=props.reply_to,
                         properties=pika.BasicProperties(correlation_id = \
                                                         props.correlation_id),
                         body=response)

class AmqpListener:
    logkey = 'metal'
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
        mlog(" [%s] Excange %s declared" %(self.logkey, self.exchange_name,))
        self.channel.queue_declare(exclusive=True,
                                  callback=self.on_queue_declared)

    def on_queue_declared(self, frame):
        mlog(" [%s] Queue declared" % (self.logkey,))
        self.queue = frame.method.queue
        self.channel.queue_bind(exchange=self.exchange_name,
                           queue=self.queue,
                           routing_key = self.routing_key,
                           callback = self.on_queue_bound)
    def on_queue_bound(self, frame):
        mlog(" [%s] Awaiting RPC requests" % (self.logkey,))
        self.channel.basic_consume(self.on_request,
                              queue=self.queue,
                              no_ack=True)

    def on_request(self, ch, method, props, body):
        if self.request_callback:
          self.request_callback(ch, method, props, body)


