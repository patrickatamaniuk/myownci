
module WorkersHelper
  def WorkersHelper.update_from_metal_alive(metal, data)
      Rails.logger.info("Update worker from metal_alive #{data}")
      return if data['host-uuid'].nil?
      name = data['nodename']
      uuid = data['host-uuid']
      state = data['state']
      capabilities = data['capabilities']
      distribution = data['distribution']
      architecture = data['architecture']
      platform = data['platform']
      system = data['system']
      worker_data = {
        :name => name,
        :state => state,
        :capabilities => "#{capabilities}",
        :distribution => "#{distribution}",
        :architecture => architecture,
        :platform => platform,
        :system => system,
#        :last_seen_at => Time.now
      }

      Rails.logger.info("Looking for worker #{uuid}")
      worker = metal.workers.find_by_uuid(uuid)
      Rails.logger.info("found worker #{worker}")
      unless worker
        worker_data[:uuid] = uuid
        metal.workers.create(worker_data)
      else
        worker.update_attributes(worker_data)
        worker.save
      end
  end

end
