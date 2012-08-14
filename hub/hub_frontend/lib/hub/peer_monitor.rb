
module Hub
  class PeerMonitor
    def initialize(channel)
      @channel = channel
    end

    def start
      queue_name = ""
      EventMachine.add_periodic_timer(Rpcserver::Application.config.peer_check_interval,
                                      &method(:check_peers))
      Rails.logger.info('[AMQP] PeerMonitor started')
    end

    def check_peers
      Rails.logger.info('[AMQP] PeerMonitor tick')
      discover_metal
    end

    def discover_metal
      exchange   = @channel.topic(Rpcserver::Application.config.broadcast_exchange_name,
                                 :auto_delete => false)
      # request configurations from metal
      EventMachine.add_timer(0.15) do
        Rails.logger.info("[AMQP] Sending metal discovery request...")
        exchange.publish("get config",
                                     :correlation_id  => Kernel.rand(10101010).to_s,
                                     :routing_key => 'ping.metal'
                                     )
      end
    end


  end
end
