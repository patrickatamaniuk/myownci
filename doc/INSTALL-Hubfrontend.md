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

Configure Apache
----------------

Sample apache vhost:

  <VirtualHost *:80>
  ServerAdmin webmaster@localhost

    DocumentRoot path_to_hub/hub_frontend/public
    PassengerMaxPoolSize 30
    PassengerPoolIdleTime 0
    RailsEnv production
    PassengerMinInstances 2

    <Directory path_to_hub/hub_frontend/public>
      PassengerResolveSymlinksInDocumentRoot on
    </Directory>

    ErrorLog ${APACHE_LOG_DIR}/error.log
    LogLevel warn
    CustomLog ${APACHE_LOG_DIR}/access.log combined

  </VirtualHost>
  PassengerPreStart http://127.0.0.1/

Important: for passenger to start up the application, the PassengerMinInstances and PassengerPreStart directive is required.
For PassengerPreStart to work with rvm and gemsets, the prestart script must be edited to use the correct ruby version:

  vi /usr/local/rvm/gems/ruby-1.9.3-p194@rpcserver/gems/passenger-3.0.15/helper-scripts/prespawn

  #!/usr/local/rvm/rubies/ruby-1.9.3-p194/bin/ruby

or whatever ruby@gemset you prefer to use.
