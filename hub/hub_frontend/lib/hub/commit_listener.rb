#see http://rdoc.info/github/ruby-amqp/amqp/master/file/docs/GettingStarted.textile
module Hub
  class CommitListener
    def initialize(channel)
      @channel = channel
    end

    def start
      queue_name = Rpcserver::Application.config.commit_queue_name
      request_queue = @channel.queue(queue_name, :durable => true)
      request_queue.subscribe(:ack => true) do |metadata, payload|
        data = {}
        data = JSON.parse(payload) if payload
        Rails.logger.info("[AMQP] Received app:\"#{metadata.app_id}\" repository_id:\"#{data['repository_id'] if data['repository_id']}\" from queue:#{queue_name}")
        RequestsHelper::create_from_push(data)
        metadata.ack
      end
    end
  end
end
