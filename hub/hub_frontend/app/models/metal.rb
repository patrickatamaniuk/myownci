class Metal < ActiveRecord::Base
  attr_accessible :last_seen_at, :name, :state, :uuid
  has_many :workers
end
