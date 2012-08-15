import platform
import subprocess
import re

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
          self.id['distribution'] = platform.linux_distribution()[:2]
        except:
          self.id['distribution'] = ('', '')
        self.id['platform'] = platform.platform() #human readable, most portable

    def get_hw_addr(self):
        for line in subprocess.check_output(['ifconfig', '-a']).split("\n"):
          hwaddr = self.hwre.search(line)
          if hwaddr:
            self.id['hwaddrlist'].append(hwaddr.group(1))
    def __str__(self):
        return repr(self.id)

