Install rabbitmq
================

The central queue can run on a dedicated server but most simple scenario would be
to run the queue on the hub server.

Installation
------------
as root:

  wget http://www.rabbitmq.com/rabbitmq-signing-key-public.asc
  apt-key add rabbitmq-signing-key-public.asc
  echo 'deb http://www.rabbitmq.com/debian/ testing main' > /etc/apt/sources.list.d/rabbitmq.list 
  apt get update
  apt-get install rabbitmq-server

lower disk limit if less than 1G disk space available

/etc/rabbitmq/rabbitmq.config:

  [
   {rabbit, [{disk_free_limit, 100000000}] }
  ].

Configuration
-------------

Default user in rabbitmq is guest.
Setup a user in rabbitmq and remove the guest user to add security to your system.

Note:
All client configurations must use the new users credentials. They use guest per default, too.
