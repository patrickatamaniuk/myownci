import sys, time
import pika
from myownci import mlog

class AmqpBase:
    logkey = 'metal'
    exchange_name = 'myownci.broadcast'
    routing_key = ['#']
    app_id = 'metal'

    def __init__(self, config):
        self.config = config.config
        self.config_object = config
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

        self.channel.exchange_declare(exchange=self.exchange_name,
                                 type='topic',
                                 callback=self.on_exchange_declared)

    def on_exchange_declared(self, frame):
        mlog(" [%s] Excange %s declared" %(self.logkey, self.exchange_name,))
        self.channel.queue_declare(exclusive=True,
                                  callback=self.on_queue_declared)

    def on_queue_declared(self, frame):
        mlog(" [%s] Queue declared" % (self.logkey,))
        self.queue = frame.method.queue
        if type(self.routing_key) == type(""):
            self.routing_key = [self.routing_key]
        self.bindcount = 0
        for routing_key in self.routing_key:
            self.channel.queue_bind(exchange=self.exchange_name,
                           queue=self.queue,
                           routing_key = routing_key,
                           callback = self.on_exchange_bound)
    def on_exchange_bound(self, frame):
        self.bindcount += 1
        if self.bindcount == len(self.routing_key):
            self.on_queue_bound(frame)

    def add_routing_key(self, routing_key, callback=None):
        self.channel.queue_bind(exchange=self.exchange_name,
                       queue=self.queue,
                       routing_key = routing_key,
                       callback = callback)

    def on_queue_bound(self, frame):
        self.on_ready()
        self.consume()

    def consume(self):
        mlog(" [%s] Awaiting RPC requests" % (self.logkey,))
        self.channel.basic_consume(self.on_request,
                              queue=self.queue,
                              no_ack=True)

    def on_ready(self):
        pass

    def on_request(self, ch, method, props, body):
        if self.request_callback:
          self.request_callback(ch, method, props, body)

    def reply(self, response, ch, props):
        #mlog(" [%s] Sending reply" % (self.logkey, ))
        ch.basic_publish(exchange='',
                         routing_key=props.reply_to,
                         properties=pika.BasicProperties(correlation_id = \
                                                         props.correlation_id),
                         body=response)

    def send(self, body, exchange_name='', routing_key='', props=None):
        mlog(" [%s] Sending %s" % (self.logkey, routing_key))
        if props is None:
          props = {}
        props['app_id'] = self.app_id
        props['timestamp'] = time.time()
        self.channel.basic_publish(exchange=exchange_name,
                      routing_key=routing_key,
                      properties=pika.BasicProperties(**props),
                      body=body)


