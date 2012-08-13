require "amqp"
require "json"

puts "Starting."
EventMachine.run do
  connection = AMQP.connect
  channel    = AMQP::Channel.new(connection)

  exchange   = channel.topic("myownci.broadcast", :auto_delete => false)

  queue = channel.queue("", :durable => true)
  queue.bind(exchange, :routing_key => "#")
  queue.subscribe() do |metadata, payload|
    puts "Got a request #{metadata.inspect}."
    puts "Got a request #{metadata.content_type}."
    puts "metadata.app_id      : #{metadata.app_id}"
    puts "metadata.routing_key : #{metadata.routing_key}"
    puts "metadata.content_type: #{metadata.content_type}"
    puts "metadata.headers     : #{metadata.headers.inspect}"
    puts "metadata.timestamp   : #{metadata.timestamp.inspect}"
    puts "metadata.delivery_tag: #{metadata.delivery_tag}"
    puts "metadata.redelivered : #{metadata.redelivered?}"
    puts "metadata.reply_to    : #{metadata.reply_to}"
    puts "metadata.correlation_id: #{metadata.correlation_id}"
    puts "payload: #{payload}"
#    data = JSON.parser.new(payload).parse()
#    data.each{|k, v|
#      puts "#{k} => #{v}"
#    }
    puts "."
  end


  Signal.trap("INT") { connection.close { EventMachine.stop } }
end
puts "End."
