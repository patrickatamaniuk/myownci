#see http://rdoc.info/github/ruby-amqp/amqp/master/file/docs/GettingStarted.textile
include MetalsHelper

module Hub
  class BroadcastListener
    def initialize(channel)
      @channel = channel
    end

    def start
      queue_name = ""
      exchange_name = Rpcserver::Application.config.broadcast_exchange_name
      routing_key = '*.hub'
      exchange = @channel.topic(exchange_name, :auto_delete => false)
      queue = @channel.queue(queue_name, :durable => true)
      queue.bind(exchange, :routing_key => routing_key)
      queue.subscribe(:ack => true) do |metadata, payload|
        data = {}
        begin
          Rails.logger.info(payload)
          data = JSON.parse(payload) if payload
        rescue
          Rails.logger.error("[AMQP] Error decoding payload")
          metadata.ack
          return
        end
        Rails.logger.info("[AMQP] Received app:\"#{metadata.app_id}\" #{metadata.routing_key}")
        case metadata.routing_key
        when 'metal_alive.hub'
          MetalsHelper::create_from_push(data)
        end
        metadata.ack
      end
      Rails.logger.info('[AMQP] BroadcastListener started')
    end
  end
end
