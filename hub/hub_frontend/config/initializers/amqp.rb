require 'json'
require 'amqp/utilities/server_type'
include RequestsHelper

if false #Disabled, we are only webserver. need to run dispatcher as separate process for now
  case AMQP::Utilities::ServerType::detect
  when :passenger then
    PhusionPassenger.on_event(:starting_worker_process) do |forked|
      require 'eventmachine'
      require 'amqp'

      if forked
        Hub::Loop::start
      end
    end
  when nil then
    #donada for rake tasks
  else # webrick, thin etc.
    require 'amqp'
    require 'eventmachine'
    Hub::Loop::start
  end
end
