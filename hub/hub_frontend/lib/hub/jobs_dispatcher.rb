module Hub
  class JobsDispatcher
    def initialize(channel)
      @channel = channel
    end

    def start
      queue_name = ""
      EventMachine.add_periodic_timer(Rpcserver::Application.config.jobs_check_interval,
                                      &method(:check_jobs))
      Rails.logger.info('[AMQP] request job started')
    end

    def check_jobs
      Rails.logger.info('[AMQP] job tick')

      jobs = Job.order('created_at').where(:state => 'new')
      jobs.each{|job|
        Rails.logger.info("new job at #{job.created_at}")
      }
    end

  end
end
