class Worker < ActiveRecord::Base
  attr_accessible :ip, :name, :snapshottag, :vmimage, :vmname,
    :last_seen_at, :uuid, :state,
    :system, :architecture, :distribution, :capabilities, :platform
  belongs_to :metal
  has_one :job
end
