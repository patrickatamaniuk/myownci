module MetalsHelper
  def create_from_push(data)
    Rails.logger.info("create_from_push #{data}")
    return unless data['envelope']
    return unless data['envelope']['host-uuid']
    uuid = data['envelope']['host-uuid']
    metal = Metal.find_by_uuid(uuid)
    unless metal
      save_data = {
        :uuid => uuid,
        :name => data['envelope']['hostname'],
        :platform => data['metal']['platform']
      }
      Rails.logger.info("New metal #{uuid}")
      metal = Metal.new(save_data)
      metal.save
    end

    Rails.logger.info("Update metal #{uuid}")
    data['workers'].each{|worker|
      name = worker['nodename']
      next if worker['host-uuid'].nil?
      uuid = worker['host-uuid']
      capabilities = worker['capabilities']
      distribution = worker['distribution']
      architecture = worker['architecture']
      platform = worker['platform']
      system = worker['system']
      worker = metal.workers.find_by_uuid(uuid)
      worker_data = {
        :uuid => uuid,
        :name => name,
        :capabilities => "#{capabilities}",
        :distribution => "#{distribution}",
        :architecture => architecture,
        :platform => platform,
        :system => system
      }
      unless worker
        metal.workers.create(worker_data)
      else
        worker.update_attributes({
          :name => name,
          :capabilities => "#{capabilities}",
          :distribution => "#{distribution}",
          :architecture => architecture,
          :platform => platform,
          :system => system
        })
        worker.save
      end
    }
  end
end
