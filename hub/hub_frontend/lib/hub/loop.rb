module Hub
  class Loop

    def self.run
      connection = AMQP.connect
      channel    = AMQP::Channel.new(connection)
      @channel = channel
      AMQP.channel ||= AMQP::Channel.new(AMQP.connection)

      queue_name = "myownci.git.commit"
      request_queue = channel.queue(queue_name, :durable => true)
      request_queue.subscribe(:ack => true) do |metadata, payload|
        data = {}
        data = JSON.parse(payload) if payload
        Rails.logger.info("[AMQP] Received app:\"#{metadata.app_id}\" repository_id:\"#{data['repository_id'] if data['repository_id']}\" from queue:#{queue_name}")
        RequestsHelper::create_from_push(data)
        metadata.ack
        discover_metal(connection)
      end
    end

    def self.discover_metal(connection)
      channel = @channel #AMQP::Channel.new(connection)

      replies_queue = channel.queue("", :exclusive => true, :auto_delete => true)
      replies_queue.subscribe do |metadata, payload|
        Rails.logger.info("[AMQP] Response for #{metadata.correlation_id}: #{payload.inspect}")
      end
      exchange   = channel.fanout("myownci.metal.discover", :auto_delete => false)
      EventMachine.add_timer(2) do
        puts "[request] Sending a request..."
        exchange.publish("30",
                                     :correlation_id  => Kernel.rand(10101010).to_s,
                                     :reply_to    => replies_queue.name,
                                     )
      end
    end

  end
end
