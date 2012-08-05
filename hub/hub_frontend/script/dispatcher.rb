#!/usr/bin/env ruby
require File.expand_path('../../config/environment', __FILE__)
require "amqp"
require "json"

require "requests_helper"

Rails.logger.info "[AMQPd] Initializing amqp..."
EventMachine.run do
  Hub::Loop.run

  Signal.trap("INT") { connection.close { EventMachine.stop } }
end
Rails.logger.info "[AMQPd] done."
