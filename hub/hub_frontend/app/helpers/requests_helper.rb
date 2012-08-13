module RequestsHelper

  def create_from_push(data)
    Rails.logger.info("Creating request from amqp push message")
    #data.each{|k, v|
    #    Rails.logger.info("#  #{k} => #{v}")
    #} if data

#    if Request.find_by_commit(data['head'])
#      Rails.logger.warn("Duplicate request for commit #{data['head']}")
#      return
#    end

    save_data = {}
    save_data[:commits] = JSON.dump(data['commits'])
    save_data[:buildconfig] = data['buildconfig']
    save_data[:ref] = data['ref']
    save_data[:commit] = data['head']
    save_data[:repo] = data['repository_id']
    data['commits'].each{|commit|
      Rails.logger.info("checking #{commit['sha']} against #{data['head']}")
      if commit['sha'] == data['head']
        Rails.logger.info("#{commit}")
        save_data[:author_name] = commit['author']['name']
        save_data[:author_email] = commit['author']['email']
        save_data[:committer_name] = commit['committer']['name']
        save_data[:committer_email] = commit['committer']['email']
        save_data[:committed_date] = Time.at(commit['committed_date'])
        break
      end
    }
    request = Request.new(save_data)
    request.save

    analyze_request(request)
  end

  def invalid_request(request, message)
      Rails.logger.error("Invalid request #{request.id} #{message}")
      Rails.logger.error(request.buildconfig)
      Rails.logger.error(cfg)
      request.state='invalid'
      request.save
  end

  def analyze_request(request)
    Rails.logger.info('analyzing request')
    cfg = request.buildconfig_parsed
    if cfg.nil? || cfg.empty?
      return invalid_request(request, 'configuration parse error')
    end

    #build matrix
    begin
      Hub::Matrix.multiply(cfg) {|job_attributes|
        unless request.jobs.create(job_attributes)
          Rails.logger.error("Failed to create job for request #{request.id}")
        end
      }
    rescue ArgumentError => exception
      return invalid_request(request, "#{exception}")
    end
    request.state = 'waiting_for_worker'
    request.save
  end

end
