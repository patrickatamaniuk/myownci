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
end
