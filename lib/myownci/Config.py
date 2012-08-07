import os
import simpleyaml

class Config:
    configfilename = 'client.yaml'

    def __init__(self, configfilename=None):
        if configfilename:
            self.configfilename = configfilename
        self.load()

    def load(self):
        self.config = {}
        for fname in [os.path.abspath(self.configfilename), os.path.join('/etc/myownci', self.configfilename)]:
          if os.path.isfile(fname):
            self.config = simpleyaml.load(open(fname).read())
            break

        self.config['var'] = {}
        try:
            self.config['var'].update(simpleyaml.load(open(os.path.join('/var/tmp', self.configfilename), 'r')))
        except IOError:
            pass

    def set_var(self, data):
        self.config['var'].update(data)
    def save(self):
        simpleyaml.dump(self.config['var'], open(os.path.join('/var/tmp', self.configfilename), 'w'))


