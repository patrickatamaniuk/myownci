#!/usr/bin/env ruby

require "amqp"
require "json"
require File.expand_path('../../../config/environment', __FILE__)

require "requests_helper"

puts "Starting."
EventMachine.run do
  connection = AMQP.connect
  channel    = AMQP::Channel.new(connection)
  queue_name = "myownci.git.commit"

  requests_queue = channel.queue(queue_name, :durable => true)
  requests_queue.subscribe(:ack => true) do |metadata, payload|
    data = {}
    data = JSON.parse(payload) if payload
    Rails.logger.info("[AMQP] Received app:\"#{metadata.app_id}\" repository_id:\"#{data['repository_id'] if data['repository_id']}\" from queue:#{queue_name}")
    RequestsHelper::create_from_push(data)

    metadata.ack
  end


  Signal.trap("INT") { connection.close { EventMachine.stop } }
end
puts "End."
