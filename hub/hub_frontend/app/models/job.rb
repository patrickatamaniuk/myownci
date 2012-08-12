class Job < ActiveRecord::Base
  belongs_to :worker
  belongs_to :request
  attr_accessible :worker, :request, :state,
    :before_install, :install, :after_install,
    :before_script, :script, :after_script,
    :language, :interpreter, :environment, :operating_system,
    :failure_allowed,
    :started_at, :finished_at
end
