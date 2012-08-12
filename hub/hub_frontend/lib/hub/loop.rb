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
          metal_listener = MetalListener.new(channel)
          metal_listener.start
          request_job = RequestJob.new(channel)
          request_job.start
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

    def self.discover_metal(channel)
      replies_queue = channel.queue("", :exclusive => true, :auto_delete => true)
      replies_queue.subscribe do |metadata, payload|
        Rails.logger.info("[response] Response for #{metadata.correlation_id}: #{payload}")
      end

      exchange   = channel.topic("myownci_discover", :auto_delete => false)
      # request configurations from metal
      EventMachine.add_timer(0.15) do
        Rails.logger.info("[AMQP] Sending metal discovery request...")
        exchange.publish("get config",
                                     :correlation_id  => Kernel.rand(10101010).to_s,
                                     :reply_to    => replies_queue.name,
                                     :routing_key => 'discover.metal'
                                     )
      end
      EventMachine.add_timer(10) {
        Rails.logger.info('[AMQP] metal discovery timeout')
      }
    end

    def self.close
      if @connection
        @connection.close()
        Rails.logger.info("[AMQP] closing connection.")
      end
    end
  end
end
