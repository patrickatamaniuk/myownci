module Hub
  class RequestJob
    def initialize(channel)
      @channel = channel
    end

    def start
      queue_name = ""
      exchange_name = 'myownci_discover'
      EventMachine.add_periodic_timer(1, &method(:check_requests))
      Rails.logger.info('[AMQP] request job started')
    end

    def check_requests
      Rails.logger.info('[AMQP] request job tick')

      requests = Request.order('created_at').where(:state => 'new')
      requests.each{|request|
        Rails.logger.info("new request at #{request.created_at}")
        analyze_request(request)
      }
    end

  end
end
