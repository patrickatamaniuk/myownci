class Metal < ActiveRecord::Base
  attr_accessible :last_seen_at, :name, :state, :uuid, :platform
  has_many :workers
end
