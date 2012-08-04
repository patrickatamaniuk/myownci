require "amqp"
require "json"

puts "Starting."
EventMachine.run do
  connection = AMQP.connect
  channel    = AMQP::Channel.new(connection)

  requests_queue = channel.queue("myownci.git.commit", :durable => true)
  requests_queue.subscribe(:ack => true) do |metadata, payload|
    puts "[commit] Got a request #{metadata.content_type}. Sending a reply..."
    puts "metadata.routing_key : #{metadata.routing_key}"
    puts "metadata.content_type: #{metadata.content_type}"
    puts "metadata.headers     : #{metadata.headers.inspect}"
    puts "metadata.timestamp   : #{metadata.timestamp.inspect}"
    puts "metadata.delivery_tag: #{metadata.delivery_tag}"
    puts "metadata.redelivered : #{metadata.redelivered?}"

    puts "metadata.app_id      : #{metadata.app_id}"
    puts
    puts "Received a message:"
    data = JSON.parser.new(payload).parse()
    data.each{|k, v|
      puts "#{k} => #{v}"
    }
    puts "."
    metadata.ack
  end


  Signal.trap("INT") { connection.close { EventMachine.stop } }
end
puts "End."
