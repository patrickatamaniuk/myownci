require 'json'
include RequestsHelper

def start_amqp_in_thread
  Rails.logger.info "[AMQP] Initializing amqp..."
  amqp_thread = Thread.new {
    failure_handler = lambda {
      Rails.logger.fatal("[AMQP] [FATAL] Could not connect to AMQP broker")
    }
    AMQP.start(:on_tcp_connection_failure => failure_handler)
  }
  amqp_thread.abort_on_exception = true
  sleep(0.15)

  EventMachine.next_tick do
    Hub::Loop::run
  end
end

if defined?(PhusionPassenger) # otherwise it breaks rake commands if you put this in an initializer
  PhusionPassenger.on_event(:starting_worker_process) do |forked|
    require 'eventmachine'
    require 'amqp'

    if forked
      start_amqp_in_thread
    end
  end
elsif defined?(::WEBrick) #when started with 'rails server'. 'rackup' does not work.
  require 'amqp'
  require 'eventmachine'
  start_amqp_in_thread
end #else rake task
