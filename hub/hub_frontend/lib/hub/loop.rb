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
      channel    = AMQP::Channel.new(connection)

      replies_queue = channel.queue("", :exclusive => true, :auto_delete => true)
      replies_queue.subscribe do |metadata, payload|
        puts "[response] Response for #{metadata.correlation_id}: #{payload}"
      end

      exchange   = channel.topic("myownci_discover", :auto_delete => false)
      # request configurations from metal
      EventMachine.add_timer(0.15) do
        puts "[request] Sending a request..."
        exchange.publish("get config",
                                     :correlation_id  => Kernel.rand(10101010).to_s,
                                     :reply_to    => replies_queue.name,
                                     :routing_key => 'discover.metal'
                                     )
      end
      EventMachine.add_timer(10) {
        puts 'timeout'
      }
    end

  end
end
