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
      if commit['sha'] == data['head']
        save_data[:author_name] = commit['author_name']
        save_data[:author_email] = commit['author_email']
        save_data[:committer_name] = commit['committer_name']
        save_data[:committer_email] = commit['committer_email']
        #save_data[:committed_date] = commit['committed_date']
        break
      end
    }
    request = Request.new(save_data)
    request.save

  end
end
