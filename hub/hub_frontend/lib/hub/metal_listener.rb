#see http://rdoc.info/github/ruby-amqp/amqp/master/file/docs/GettingStarted.textile
module Hub
  class MetalListener
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
        data = JSON.parse(payload) if payload
        Rails.logger.info("[AMQP] Received app:\"#{metadata.app_id}\" repository_id:\"#{data['repository_id'] if data['repository_id']}\" from queue:#{queue_name}")
        metadata.ack
      end
      Rails.logger.info('[AMQP] bound metal exchange listener')
    end
  end
end
