#!/usr/bin/env python
#
# installation:
# sudo apt-get install python-pip
# sudo pip install myownci_pysupport
# sudo pip install simpleyaml
# sudo pip install pika
import simplejson
import time

from myownci.Config import Config
from myownci.Identity import Identity
from myownci.Amqp import AmqpBase
from myownci.IntervalScheduler import IntervalScheduler
from myownci import mlog

class Worker(AmqpBase):
    logkey = 'worker'
    routing_key = ['*.worker']
    app_id = 'worker'
    tick_interval = 5
    request_timeout = 56

    def __init__(self, config):
        self.state = 'unconfigured'
        self.uuid = None
        self.heartbeat = None
        self.identity = Identity()

        self.timeouts = {}

        config.set_var({'identity' : self.identity.id})
        config.save()

        for hwaddr in self.identity.id['hwaddrlist']:
            self.routing_key.append("*.%s"%hwaddr)

        try:
            self.uuid = config.config['var']['uuid'],
            self.routing_key.append("*.%s"%self.uuid)
        except KeyError:
            self.uuid = None

        AmqpBase.__init__(self, config)

    def on_connected(self, connection):
        self.heartbeat = IntervalScheduler(connection, callback=self.tick, interval=self.tick_interval)
        AmqpBase.on_connected(self, connection)
        self.enter_state('connected')

    def on_ready(self):
        if not self.uuid:
            self.enter_state('request_uuid')
        else:
            self.enter_state('configured')

    def on_request(self, ch, method, props, body):
        mlog(" [%s] Got request %r" % (self.logkey, method.routing_key))

        dst = method.routing_key.split('.')[1]
        cmd = method.routing_key.split('.')[0]

        if dst in self.identity.id['hwaddrlist'] + [self.uuid]:
            #update command from metal
            if 'update_config' == cmd:
                body = simplejson.loads(body)
                self.update_config(body)

        #ping request from metal
        elif 'ping' == cmd:
            self.ping_reply()
        else:
            mlog(" [%s] Unknown request %r" % (self.logkey, method.routing_key))

    def send_alive(self):
        self.ping_reply(routing_key='worker_alive.metal')
        self.timeouts['send_alive'] = time.time()+240

    def request_job(self):
        self.timeouts['request_job'] = time.time()+self.request_timeout
        self.ping_reply(routing_key='worker_requests_job.hub')

    def ping_reply(self, routing_key='worker_ping_reply.metal'):
        data = {}
        data['envelope'] = {
            'host-uuid': self.uuid,
            'nodenamename': self.config['var']['identity']['nodename'],
        }
        data.update({'worker':self.config['var']['identity']})
        data['worker']['capabilities'] = self.config['capabilities']
        data['worker']['state'] = self.state
        self.send(simplejson.dumps(data),
            exchange_name = self.exchange_name,
            routing_key = routing_key,
            props = { 'content_type': 'application/json' })
        #mlog(" [%s] Sent %r:%r" % (self.logkey, routing_key, repr(data)))

    def update_config(self, body):
        mlog(" [%s] got uuid %s" % (self.logkey, body['host-uuid']))
        self.uuid = body['host-uuid']
        self.config_object.set_var({'uuid' : self.uuid})
        self.config_object.save()
        self.add_routing_key("*.%s" % (self.uuid, ))
        routing_key = "*.%s" % (self.uuid, )
        #mlog(" [%s] added routing key %s" % (self.logkey, routing_key))
        self.enter_state('configured')

    def tick(self):
        mlog(" [%s] tick  state: %s" % (self.logkey, self.state))
        now = time.time()
        for k, t in self.timeouts.items():
            if now > t:
                mlog(" [%s] timeout for %s" % (self.logkey, k))
                del self.timeouts[k]
                if k == 'request_job':
                    self.enter_state('configured')
                elif k == 'send_alive':
                    self.send_alive()

    def enter_state(self, state):
        self.state = state
        mlog(" [%s] enter state: %s" % (self.logkey, self.state))
        if state == 'configured':
            self.connection.add_timeout(1, self.send_alive)
            self.enter_state('request_job')
        elif state == 'request_uuid':
            self.connection.add_timeout(1, self.send_alive)
        elif state == 'request_job':
            self.connection.add_timeout(1, self.request_job)

def main():
    config = Config('worker.yaml')
    Worker(config)

if __name__ == '__main__':
  main()
