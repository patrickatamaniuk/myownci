class Worker < ActiveRecord::Base
  attr_accessible :ip, :name, :snapshottag, :vmimage, :vmname
end
