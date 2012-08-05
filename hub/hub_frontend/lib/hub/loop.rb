module Hub
  class Loop
    def self.run
      AMQP.channel ||= AMQP::Channel.new(AMQP.connection)

      queue_name = "myownci.git.commit"
      AMQP.channel.queue(queue_name, :durable => true).subscribe(:ack => true) do |metadata, payload|
        data = {}
        data = JSON.parse(payload) if payload
        Rails.logger.info("[AMQP] Received app:\"#{metadata.app_id}\" repository_id:\"#{data['repository_id'] if data['repository_id']}\" from queue:#{queue_name}")
        RequestsHelper::create_from_push(data)
        metadata.ack
      end
    end
  end
end
