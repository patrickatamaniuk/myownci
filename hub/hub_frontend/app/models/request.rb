class Request < ActiveRecord::Base
  attr_accessible :commit, :created, :repo,
    :buildconfig, :commits, :ref, :author_name, :author_email, :committer_name, :committer_email,
    :committed_date
end
