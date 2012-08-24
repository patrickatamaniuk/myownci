import time
import types
from logging import debug, warning
from myownci.IntervalScheduler import IntervalScheduler

class UnhandledStateException(Exception): pass
class UnhandledEventException(Exception): pass

class StateEngine:
    states = None
    state = None
    last_state = None
    tick_interval = 5

    def __init__(self, states, initialstate=None):
        self.state = initialstate
        self.states = states
        self.__timeouts = {}
        self.heartbeat = None

    def event(self, event, *args, **kwargs):
        debug(' -- event %r %r %r', event, 'state', self.state)
        state = self.state
        if event not in self.states:
            if '*' not in self.states:
                raise UnhandledEventException(event)
            event = '*'
        if state not in self.states[event]:
            if '*' not in self.states[event]:
                raise UnhandledStateException("%s %s"% (self.state, event))
            state = '*'
        action = self.states[event][state]
        if 'nextstate' in action:
            self.set_state(action['nextstate'])
            methodname = "on_state_%s"%self.state
            if hasattr(self, methodname):
                method = getattr(self, "on_state_%s"%self.state)
                debug(' -- calling method %r', method)
                method(*args, **kwargs)
        if 'cmd' in action:
            self.__call_cmd(action['cmd'], *args, **kwargs)

        if 'timeout' in action:
            debug("ADDING TIMEOUT %r", self.state+'_timeout')
            self.remove_timeout(self.state+'_timeout')
            state = self.state
            self.add_timeout(state+'_timeout', action['timeout'], self.event, state+'_timeout')

    def __call_cmd(self, command, *args, **kwargs):
        debug(' -- call cmd %r', command)
        if type(command) == types.ListType:
            for c in command:
                self.__call_cmd(c, *args, **kwargs)
            return
        timeout = 0
        if type(command) == types.TupleType:
            if len(command) > 2:
                args = command[2]
            if len(command) > 3:
                kwargs = command[3]
            delay = command[0]
            command = command[1]
        if type(command) == types.MethodType:
            self.defer(delay, command, *args, **kwargs)

    def set_state(self, state):
        debug(' -- setting state to %r', state)
        self.last_state = self.state
        self.state = state

    def get_state(self):
        return self.state

    def start_timeouts(self, connection):
        self.heartbeat = IntervalScheduler(connection, callback=self.tick, interval=self.tick_interval)
    def add_timeout(self, key, seconds, callback, *args, **kwargs):
        debug(' -- add_timeout %r %r %r', key, seconds, self)
        self.__timeouts[key] = { 'when':time.time()+seconds, 'cmd':callback, 'args':args, 'kwargs':kwargs }
        debug(' -- add_timeout timeouts %r %r', self.__timeouts, self)
    def remove_timeout(self, key):
        if key in self.__timeouts:
            debug(' -- del timeout %r %r', key, self.__timeouts)
            del self.__timeouts[key]

    def tick(self):
        debug(" [%s] tick  state: %s" % (self.logkey, self.state))
        now = time.time()
        debug(' -- tick %r %r %r', now, self.__timeouts, self)
        for k, t in self.__timeouts.items():
            if now > t['when']:
                warning(" [%s] timeout for %s" % (self.logkey, k))
                if 'cmd' in t:
                    args=[]
                    kwargs={}
                    if 'args' in t:
                        args = t['args']
                    if 'kwargs' in t:
                        kwargs = t['kwargs']
                    self.defer(0.1, t['cmd'], *args, **kwargs)
                debug(' -- del timeout %r %r', k, self.__timeouts)
                del self.__timeouts[k]

if __name__ == '__main__':
    class stest(StateEngine):
        def __init__(self):
            StateEngine.__init__(self,{
                '*': { '*': { 'nextstate':'s1' }
                },
                'e1': { 's1': {'cmd':self.c1, 'nextstate':'s2' },
                        '*':  {'cmd':self.c2, 'nextstate':'s1' },
                },
            }, 's0')

        def e1(self):
            self.event('e1')
        def c1(self):
            print 'c1'
        def c2(self):
            print 'c2'

    t = stest()
    t.e1()
    t.e1()
    t.e1()
    t.e1()
    t.set_state('s99')
    t.e1()
    t.e1()
    t.event('e9')
