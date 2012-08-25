#see http://rdoc.info/github/ruby-amqp/amqp/master/file/docs/GettingStarted.textile
require "metals_helper"

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
          Rails.logger.debug("Hub::BroadcastListener request payload: #{payload}")
          data = JSON.parse(payload) if payload
        rescue
          Rails.logger.error("[AMQP] Error decoding payload")
          metadata.ack
          return
        end
        Rails.logger.info("[AMQP] Received app:\"#{metadata.app_id}\" #{metadata.routing_key}")

        case metadata.routing_key
        when 'metal_alive.hub'
          MetalsHelper.create_from_metal_alive(data)
        when 'worker_requests_job.hub'
          dispatch_job(data)
        end
        metadata.ack
      end
      Rails.logger.info('[AMQP] BroadcastListener started')
    end

    def dispatch_job(data)
      uuid = data['envelope']['host-uuid']
      workrequest = {
        :host_uuid => uuid,
        :capabilities => data['worker']['capabilities'],
        :distribution => data['worker']['distribution'],
        :architecture => data['worker']['architecture']
      }
      worker = Worker.find_by_uuid(uuid)
      Rails.logger.debug("Worker #{worker} requests job #{workrequest}")
      if worker.nil?
        Rails.logger.info("Request from unknown worker #{uuid}")
        ping_worker(uuid)
        return
      end
      job_candidates = Job.find(:all, :conditions=>{
        :language => workrequest[:capabilities],
        :state => 'new'
      });
      job_candidates.each{|job|
        Rails.logger.info("Job candidate: #{job}")
      }
    end

    def ping_worker(uuid)
    end

  end
end
