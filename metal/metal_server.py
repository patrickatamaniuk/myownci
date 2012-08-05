#!/usr/bin/env python
import pika

connection = pika.BlockingConnection(pika.ConnectionParameters(
        host='localhost'))

channel = connection.channel()

channel.exchange_declare(exchange='myownci.metal.discover',
                         type='fanout')

result = channel.queue_declare(exclusive=True)
queue_name = result.method.queue

def fib(n):
    if n == 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fib(n-1) + fib(n-2)

def on_request(ch, method, props, body):
    n = int(body)

    print " [.] fib(%s)"  % (n,)
    response = fib(n)

    ch.basic_publish(exchange='',
                     routing_key=props.reply_to,
                     properties=pika.BasicProperties(correlation_id = \
                                                     props.correlation_id),
                     body=str(response))
    #ch.basic_ack(delivery_tag = method.delivery_tag)

channel.queue_bind(exchange='myownci.metal.discover',
                   queue=queue_name)

print " [x] Awaiting RPC requests"
channel.basic_consume(on_request,
                      queue=queue_name,
                      no_ack=True)

channel.start_consuming()
