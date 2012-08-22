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
from myownci.StateEngine import StateEngine
from myownci import mlog

class Worker(AmqpBase, StateEngine):
    logkey = 'worker'
    routing_key = ['*.worker']
    app_id = 'worker'
    tick_interval = 5
    request_timeout = 56
    stateengine = None

    def __init__(self, config):
        StateEngine.__init__(self, {
            'ev_connected':{
                '*': {},
                'unconfigured': {'nextstate':'connected'},
            },
            'ev_amqpready': {
                '*': {},
                'unconfigured': {'nextstate':'ready'},
                'connected': {'nextstate':'ready'},
            },
            'ev_request_uuid': {
                '*': {},
                'ready': {'nextstate':'request_uuid'},
            },
            'ev_configured': {
                '*': {'nextstate':'configured'},
            },
            'ev_request_job': {
                'configured': {'nextstate':'request_job'}
            },
            'timeout': {
                'request_job': {}
            }
        }, 'unconfigured')

        self.uuid = None
        self.heartbeat = None
        self.identity = Identity()

        self.timeouts = {}

        config.set_var({'identity' : self.identity.id})
        config.save()

        for hwaddr in self.identity.id['hwaddrlist']:
            self.routing_key.append("*.%s"%hwaddr)

        try:
            self.uuid = config.config['var']['uuid']
            self.routing_key.append("*.%s"%self.uuid)
        except KeyError:
            self.uuid = None

        AmqpBase.__init__(self, config)

    def on_connected(self, connection):
        self.heartbeat = IntervalScheduler(connection, callback=self.tick, interval=self.tick_interval)
        AmqpBase.on_connected(self, connection)
        self.event('ev_connected')

    def on_ready(self):
        self.event('ev_amqpready')
    def on_state_ready(self):
        if not self.uuid:
            self.event('ev_request_uuid')
        else:
            self.event('ev_configured')

    def on_request(self, ch, method, props, body):
        mlog(" [%s] Got request %r" % (self.logkey, method.routing_key))

        dst = method.routing_key.split('.')[1]
        cmd = method.routing_key.split('.')[0]

        if dst in self.identity.id['hwaddrlist'] + [self.uuid]:
            #update command from metal
            if 'update_config' == cmd:
                body = simplejson.loads(body)
                self.cmd_update_config(body)

        #ping request from metal
        elif 'ping' == cmd:
            self.cmd_ping()
        else:
            mlog(" [%s] Unknown request %r" % (self.logkey, method.routing_key))

    def on_state_request_uuid(self):
        self.add_timeout('request_uuid', 15, self.on_state_request_uuid)
        self.send_message(routing_key='worker_request_uuid.metal')

    def on_state_configured(self):
        self.connection.add_timeout(1, self.cmd_send_alive)
        self.event('ev_request_job')

    def on_state_request_job(self):
        self.add_timeout('request_job', self.request_timeout, self.on_timeout_request_job)
        self.send_message(routing_key='worker_requests_job.hub')
    def on_timeout_request_job(self):
        self.on_state_request_job()

    def cmd_send_alive(self):
        self.add_timeout('send_alive', 240, self.cmd_send_alive)
        self.send_message(routing_key='worker_alive.metal')

    def cmd_ping(self):
        self.send_message(routing_key='worker_ping_reply.metal')

    def send_message(self, routing_key='worker_ping_reply.metal'):
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
        mlog(" [%s] Sent %r:%r" % (self.logkey, routing_key, repr(data)))

    def cmd_update_config(self, body):
        mlog(" [%s] got uuid %s" % (self.logkey, repr(body['host-uuid'])))
        self.remove_timeout('request_uuid')
        print "UPDATE self.uuid", body['host-uuid']
        self.uuid = body['host-uuid']
        self.config_object.set_var({'uuid' : self.uuid})
        self.config_object.save()
        self.add_routing_key("*.%s" % (self.uuid, ))
        routing_key = "*.%s" % (self.uuid, )
        #mlog(" [%s] added routing key %s" % (self.logkey, routing_key))
        self.event('ev_configured')

    def add_timeout(self, key, seconds, callback):
        self.timeouts[key] = { 'when':time.time()+seconds, 'cmd':callback }
    def remove_timeout(self, key):
        if key in self.timeouts:
            del self.timeouts[key]

    def tick(self):
        mlog(" [%s] tick  state: %s" % (self.logkey, self.state))
        now = time.time()
        for k, t in self.timeouts.items():
            if now > t['when']:
                mlog(" [%s] timeout for %s" % (self.logkey, k))
                if 'cmd' in t:
                    t['cmd']()
                del self.timeouts[k]

def main():
    config = Config('worker.yaml')
    Worker(config)

if __name__ == '__main__':
  main()
