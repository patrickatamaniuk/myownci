#!/usr/bin/env ruby
require File.expand_path('../../config/environment', __FILE__)
require "amqp"
require "json"

require "requests_helper"

Rails.logger.info "[AMQPd] Environment ready."

t = Hub::Loop::start
Rails.logger.info "[AMQPd] threads running."

t.join() if t
Rails.logger.info "[AMQPd] done."
