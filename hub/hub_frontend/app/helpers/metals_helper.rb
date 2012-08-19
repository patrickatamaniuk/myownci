include WorkersHelper

module MetalsHelper
  def create_from_push(data)
    Rails.logger.info("create_from_push #{data}")
    return unless data['envelope']
    return unless data['envelope']['host-uuid']
    uuid = data['envelope']['host-uuid']
    save_data = {
      :name => data['envelope']['hostname'],
      :platform => data['metal']['platform'],
      :state => data['metal']['state'],
      :last_seen_at => Time.now
    }

    metal = Metal.find_by_uuid(uuid)
    unless metal
      save_data[:uuid] = uuid
      metal = Metal.new(save_data)
      metal.save
    else
      metal.update_attributes(save_data)
      metal.save
    end

    data['workers'].each{|worker_data|
      WorkersHelper::update_from_metal_alive(metal, worker_data)
    }
  end
end
