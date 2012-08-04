myownci
=======

Continuous Integration Framework for linux using kvm build guests intended for private use.

Scenario: you have private self-hosted git repositories and want to run your own ci build farm.

The plan:

Concept
=======

System layout:

    repository     hub           management server vmhost         worker vm
    commit-hook -> ampq queue -> analyzer ->       kvm control -> job control

Installation
============

Repository hook
---------------

Install git/hooks/post-receive into your repository hooks, make it executable

Configure repository identification

Hub
---

* deploy rabbitmq server

Note: Vm hosts, Worker vms and Management server need ampq access to this host.
Can run on git server

Management server
-----------------

* setup hub frontend
  rvm/ruby/rails/passenger

Vm hosts
--------

* deploy vm host control software

Needs to be on the bare host system as it will start/shutdown/reset vm guests.

Worker vms
----------

* define qemu guests
* prepare vm images
* snapshot each image

Minimal Requirements:

* python2.7

Setup and Configuration
=======================

Define Vm hosts
---------------

Define Worker vms
-----------------


