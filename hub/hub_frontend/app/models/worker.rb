class Worker < ActiveRecord::Base
  attr_accessible :ip, :name, :snapshottag, :vmimage, :vmname,
    :last_seen_at, :uuid, :state,
    :system, :architecture, :distribution, :capabilities
  belongs_to :metal
end
