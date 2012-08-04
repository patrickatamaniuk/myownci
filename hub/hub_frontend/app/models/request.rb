class Request < ActiveRecord::Base
  attr_accessible :commit, :created, :repo
end
