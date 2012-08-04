class Job < ActiveRecord::Base
  belongs_to :worker
  attr_accessible :commit, :finished, :repo, :running, :started, :success, :worker
end
