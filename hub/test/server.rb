require "amqp"

EventMachine.run do
  connection = AMQP.connect
  channel    = AMQP::Channel.new(connection)

  requests_queue = channel.queue("myownci.git.commit", :durable => true)
  requests_queue.subscribe(:ack => true) do |metadata, payload|
    puts "[requests] Got a request #{metadata}. Sending a reply..."
    puts "#{payload}"
    channel.default_exchange.publish(Time.now.to_s,
                                     :routing_key    => metadata.reply_to,
                                     :correlation_id => metadata.message_id,
                                     :immediate      => true,
                                     :mandatory      => true)

    metadata.ack
  end


  Signal.trap("INT") { connection.close { EventMachine.stop } }
end
