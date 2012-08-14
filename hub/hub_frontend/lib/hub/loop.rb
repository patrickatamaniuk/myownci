require 'amqp/utilities/event_loop_helper'

module Hub
  class Loop
    def self.start
      Rails.logger.info "[AMQP] Initializing amqp thread."
      t = AMQP::Utilities::EventLoopHelper.run do
        AMQP.start{|connection|
          @connection = connection
          channel    = AMQP::Channel.new(connection)
          commit_listener = CommitListener.new(channel)
          commit_listener.start
          broadcast_listener = BroadcastListener.new(channel)
          broadcast_listener.start
          jobs_dispatcher = JobsDispatcher.new(channel)
          jobs_dispatcher.start
          peer_monitor = PeerMonitor.new(channel)
          peer_monitor.start
        }
      end
      #t.abort_on_exception = true if t
      die_gracefully_on_signal
      t
    end
    def self.die_gracefully_on_signal
        Signal.trap("INT")  { EM.stop; self.close() }
        Signal.trap("TERM") { EM.stop; self.close() }
    end

    def self.close
      if @connection
        @connection.close()
        Rails.logger.info("[AMQP] closing connection.")
      end
    end
  end
end
