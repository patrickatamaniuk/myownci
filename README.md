myownci
=======

Continuous Integration Framework for linux using kvm build guests intended for private use.

Scenario: you have private self-hosted git repositories and want to run your own ci build farm.

The plan:

Concept
=======

System layout:

    repository     hub           management server vmhost         worker vm
    commit-hook -> amqp queue -> analyzer ->       kvm control -> job control

Installation
============

Hub
---

* deploy rabbitmq server

Note: Vm hosts, Worker vms and Management server need amqp access to this host.
Can run on git server

Management server
-----------------

* setup hub frontend
  rvm/ruby/rails/passenger

Vm hosts
--------

* deploy vm host control software

Needs to be on the bare host system as it will start/shutdown/reset vm guests.

Requirements:

* python2.7
* pip
* simpleyaml
* simplejson
* pike

Worker vms
----------

* define qemu guests
* prepare vm images
* snapshot each image

Minimal Requirements:

* python2.7
* pip
* simpleyaml
* simplejson
* pike

Setup and Configuration
=======================

Repository hook
---------------

Prerequisites:

    sudo apt-get install python-pip
    sudo pip install gitpython
    sudo pip install pike

Install git/hooks/post-receive into your repository hooks, make it executable

Configure repository identification (on the git repository server which is pushed to)

    git config --add myownci.repository-id the_unique_name_which_is_configured_in_management_server
    git config --add myownci.hub-addr ip_or_fqdn_of_amqp_host
    git config --add myownci.project-configfile .travis.yml_compatible_build_description

Example:

    project-configfile = .travis.yml
    hub-addr = 127.0.0.1
    repository-id = myownci@git-home


Define Vm hosts
---------------

Vm hosts are defined by auto-discovery

Define Worker vms
-----------------

Worker vms are defined by auto-discovery

