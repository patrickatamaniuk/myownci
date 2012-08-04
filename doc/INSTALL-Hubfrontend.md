Installing the Hub web service
==============================

Have rvm available, use a nice gemset.

Install prerequisites for passenger
-----------------------------------

Installation instructions for required software

* To install Curl development headers with SSL support:
    Please run apt-get install libcurl4-openssl-dev or libcurl4-gnutls-dev, whichever you prefer.

* To install Apache 2 development headers:
    Please run apt-get install apache2-prefork-dev as root.

* To install Apache Portable Runtime (APR) development headers:
    Please run apt-get install libapr1-dev as root.

* To install Apache Portable Runtime Utility (APU) development headers:
    Please run apt-get install libaprutil1-dev as root.

Instal passenger itself:

    gem install passenger
    rvmsudo passenger-install-apache2-module

Configure and enable passenger.load apache module

put into /etc/apache2/mods-available/passenger.load:

    LoadModule passenger_module /usr/local/rvm/gems/ruby-1.9.3-p194@rpcserver/gems/passenger-3.0.15/ext/apache2/mod_passenger.so
    PassengerRoot /usr/local/rvm/gems/ruby-1.9.3-p194@rpcserver/gems/passenger-3.0.15
    PassengerRuby /usr/local/rvm/wrappers/ruby-1.9.3-p194@rpcserver/ruby

and

    sudo a2enmod passenger
