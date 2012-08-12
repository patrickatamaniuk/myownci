class Request < ActiveRecord::Base
  attr_accessible :commit, :repo,
    :buildconfig, :commits, :ref, :author_name, :author_email, :committer_name, :committer_email,
    :committed_date

  has_many :jobs

  def buildconfig_parsed
    begin
      return YAML::load(buildconfig)
    rescue
      return nil
    end
  end
end
