#!/usr/bin/env python
#
# installation:
# sudo apt-get install python-pip
# sudo pip install simpleyaml
# sudo pip install amqp

import os, sys
import subprocess
import re
import platform
import simpleyaml

class Identity:
    hwre = re.compile('HWaddr ([0-9a-zA-Z:]+)', re.M)
    id = {}

    def __init__(self):
        self.id['hwaddrlist'] = []
        self.get_hw_addr()
        uname = platform.uname()
        self.id['system'] = uname[0]
        self.id['nodename'] = uname[1]
        self.id['processor'] = uname[5]
        self.id['architecture'], self.id['exeformat'] = platform.architecture()
        try:
          self.id['distribution'] = [x for x in platform.linux_distribution()]
        except:
          self.id['distribution'] = ('?', '?', '?')

    def get_hw_addr(self):
        for line in subprocess.check_output(['ifconfig', '-a']).split("\n"):
          hwaddr = self.hwre.search(line)
          if hwaddr:
            self.id['hwaddrlist'].append(hwaddr.group(1))
    def __str__(self):
        return repr(self.id)

class Config:
    def __init__(self):
        self.config = {}
        for fname in [os.path.abspath('worker.yaml'), '/etc/myownci/worker.yaml']:
          if os.path.isfile(fname):
            self.config = simpleyaml.load(open(fname).read())
            break
        self.config['identity'] = Identity().id
        print self.config
        simpleyaml.dump(self.config, open('worker.yaml', 'w'))

def main():
    Config()

if __name__ == '__main__':
  main()
