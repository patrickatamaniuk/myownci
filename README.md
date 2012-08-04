myownci
=======

Continuous Integration Framework for linux using kvm build guests

Concept
=======

system layout::

	repository     hub           management server vmhost         worker vm
	commit-hook -> ampq queue -> analyzer ->       kvm control -> job control

Installation
============

1. Repository hook

Install git/hooks/post-receive into your repository hooks, make it executable
Configure repository identification

