#!/usr/bin/env python
#
# installation:
# sudo apt-get install python-pip
# sudo pip install myownci_pysupport
# sudo pip install simpleyaml
# sudo pip install amqp

from myownci.Config import Config
from myownci.Identity import Identity

def main():
    config = Config('worker.yaml')
    config.set_var({'identity' : Identity().id})
    print config.config
    config.save()

if __name__ == '__main__':
  main()
