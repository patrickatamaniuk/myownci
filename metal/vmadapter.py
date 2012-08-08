import subprocess, re, sys, time
from xml.etree import ElementTree
import libvirt

class VmBase:
	def __init__(self):
		self.guests = {}

	def ls(self):
		return self.guests
	def start(self, guest):
		return False
	def stop(self, guest):
		return False
	def resetsnapshot(self, guest, snap):
		return False

class VmKVM(VmBase):
    def __init__(self):
        self.virshlistre = re.compile(r'\s+(\S+)\s+(\S+)\s+(.+)')
        VmBase.__init__(self)

    def ls(self):
        """implement ls using shell since older libvirt api does not provide listAllDomains.
            also use shell virsh dumpxml to get inspection without root privileges"""
        guests = {}
        for line in subprocess.check_output(['virsh', 'list', '--all']).split("\n"):
            if 'Name' in line: continue
            if '---' in line: continue
            mo = self.virshlistre.match(line)
            if not mo: continue
            guests[mo.group(2).strip()] = {'name': mo.group(2).strip(), 'state': mo.group(3).strip()}

        for domain_name in guests:
            print repr(domain_name)
            xml = subprocess.check_output(['virsh', 'dumpxml', domain_name])
            domxml = ElementTree.XML(xml)

            self.guests[domain_name] = {}
            self.guests[domain_name]['name'] = domxml.find('name').text
            self.guests[domain_name]['uuid'] = domxml.find('uuid').text
            self.guests[domain_name]['hwaddr'] = []
            for interfacexml in domxml.find('devices').findall('interface'):
                mac = interfacexml.find('mac')
                if 'address' in mac.keys():
                    self.guests[domain_name]['hwaddr'].append(mac.get('address'))
        return self.guests

    def start(self, guest):
        return subprocess.call(['virsh', 'start', guest])

    def stop(self, guest):
        return subprocess.call(['virsh', 'shutdown', guest])

    def __destroy(self, guest):
        return subprocess.call(['virsh', 'destroy', guest])

    def domstate(self, guest):
        try:
            state = subprocess.check_output(['virsh', 'domstate', guest])
        except:
            return 'unknown'
        return state.strip()

    def reset_guest_to_snap(self, guest, snapshotname, imgfile):
        state = self.domstate(guest)
        if state != 'shut off':
            self.__destroy(guest)
        while state != 'shut off':
            print 'waiting'
            time.sleep(1)
            state = self.domstate(guest)
        print state
        print 'applying snapshot', snapshotname, imgfile
        print subprocess.check_output(['sudo', 'kvm-img', 'snapshot', '-a', snapshotname, imgfile])

if __name__ == '__main__':
	v = VmKVM()
	print v.ls()
	v.reset_guest_to_snap('precise-ci', 'v0.1.7', '/var/lib/libvirt/images/precise-ci.img')
