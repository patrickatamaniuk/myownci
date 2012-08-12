module RequestsHelper

  def create_from_push(data)
    Rails.logger.info("Creating request from amqp push message")
    data.each{|k, v|
        Rails.logger.info("#  #{k} => #{v}")
    } if data

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

  end

  def invalid_request(request, message)
      Rails.logger.error("Invalid request #{request.id} #{message}")
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
    Rails.logger.info(request.buildconfig)
    Rails.logger.info(cfg)
    operatingsystem = cfg['os'] || ['Ubuntu 12.04']
    case cfg['language']
    when 'ruby'
      interpreters = cfg['rvm'] || "1.9.3"
      interpreter_key = 'rvm'
    when 'python'
      interpreters = cfg['python'] || "2.7"
      interpreter_key = 'python'
    else
      return invalid_request(request, "invalid language: #{cfg['language']}")
    end

    request.state = 'analyzed'
    request.save

    environments = cfg['env'] || [""]

    allow_failures = cfg['matrix']['allow_failures']
    exclude = cfg['matrix']['exclude']
    #includes = cfg['matrix']['include'] #not supported yet

    Rails.logger.info("Build: language #{cfg['language']}")
    operatingsystem.each{|os|
      interpreters.each{|interpreter|
        environments.each{|environment|
          data = {'os'=>os, interpreter_key=>interpreter, 'env'=>environment}
          next if matrix_match exclude, data
          failure_allowed = matrix_match allow_failures, data

          attributes = {
            :script => cfg['script'],
            :before_script => cfg['before_script'],
            :after_script => cfg['after_script'],
            :install => cfg['install'],
            :before_install => cfg['before_install'],
            :after_install => cfg['after_install'],
            :operating_system => os,
            :language => cfg['language'],
            :interpreter => interpreter,
            :environment => environment,
            :failure_allowed => failure_allowed
          }
          if not request.jobs.create(attributes)
            Rails.logger.error("Failed to create job for request #{request.id}")
          end
        }
      }
    }
    request.state = 'waiting'
    request.save
  end

  def matrix_match(exclude, data)
    exclude.each{|exclude_term|
      match = true
      exclude_term.each{|key, val|
        if val != data[key]
          match = false
        end
      }
      return true if match
    }
    return false
  end
end
