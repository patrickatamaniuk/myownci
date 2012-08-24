#!/usr/bin/env python
#
# installation:
# sudo apt-get install python-pip
# sudo pip install myownci_pysupport
# sudo pip install simpleyaml
# sudo pip install pika
import simplejson
import logging
from logging import info, warning, error, debug
from myownci.Config import Config
from myownci.Identity import Identity
from myownci.Amqp import AmqpBase
from myownci.StateEngine import StateEngine


class Worker(AmqpBase, StateEngine):
    logkey = 'worker'
    routing_key = ['*.worker']
    app_id = 'worker'
    request_job_timeout = 56
    alive_timeout = 240

    def __init__(self, config):
        StateEngine.__init__(self, {
            'ev_amqpready': {
                '*': {},
                'unconfigured': {'nextstate':'ready'},
            },
            'ev_request_uuid': {
                '*': {},
                'ready': {
                    'nextstate':'request_uuid',
                    'cmd': [
                        (0, self.send_message, [], {'routing_key':'worker_request_uuid.metal'})
                    ],
                    'timeout': 6
                },
            },
            'request_uuid_timeout': {
                '*':{ 'nextstate':'ready' }
            },
            'ev_configured': {
                '*': {
                    'nextstate':'configured',
                    'cmd': [
                        (0, self.cmd_send_alive),
                        (2, self.event, ['ev_request_job'])
                    ]
                },
            },
            'ev_request_job': {
                '*': {'cmd':lambda :warning("ev_request_job while", self.state)},
                'configured': {
                    'nextstate':'request_job', 
                    'cmd': (0, self.send_message, [], {'routing_key':'worker_requests_job.hub'}),
                    'timeout': self.request_job_timeout
                }
            },
            'request_job_timeout': {
                '*': {},
                'request_job': {
                    'nextstate':'configured',
                    'cmd': (0.1, self.event, ['ev_request_job'])
                }
            },
        }, 'unconfigured')

        self.uuid = None
        self.identity = Identity()

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

    def on_ready(self):
        self.start_timeouts(self.connection)
        self.event('ev_amqpready')

    def on_state_ready(self):
        if not self.uuid:
            self.event('ev_request_uuid')
        else:
            self.event('ev_configured')

    def on_request(self, ch, method, props, body):
        info(" [%s] Got request %r" % (self.logkey, method.routing_key))

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
            warning(" [%s] Unknown request %r" % (self.logkey, method.routing_key))

    def cmd_send_alive(self):
        self.add_timeout('send_alive', self.alive_timeout, self.cmd_send_alive) #loop
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
        info(" [%s] Sent %r" % (self.logkey, routing_key))

    def cmd_update_config(self, body):
        info(" [%s] got uuid %s" % (self.logkey, repr(body['host-uuid'])))
        self.remove_timeout('request_uuid')
        debug( "UPDATE self.uuid %r", body['host-uuid'])
        self.uuid = body['host-uuid']
        self.config_object.set_var({'uuid' : self.uuid})
        self.config_object.save()
        self.add_routing_key("*.%s" % (self.uuid, ))
        routing_key = "*.%s" % (self.uuid, )
        #debug(" [%s] added routing key %s" % (self.logkey, routing_key))
        self.event('ev_configured')


def main():
    logging.basicConfig(level=logging.DEBUG)
    config = Config('worker.yaml')
    Worker(config)

if __name__ == '__main__':
  main()
