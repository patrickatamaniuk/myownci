class RemoveRequestfieldsFromJobs < ActiveRecord::Migration
  def up
    remove_column :jobs, :commit
    remove_column :jobs, :repo
    remove_column :jobs, :running
    remove_column :jobs, :success
    remove_column :jobs, :scripts
    remove_column :jobs, :required_environment
    remove_column :jobs, :required_language
    remove_column :jobs, :required_os
    remove_column :jobs, :started
    remove_column :jobs, :finished
  end

  def down
    add_column :jobs, :started, :datetime
    add_column :jobs, :finished, :datetime
    add_column :jobs, :required_os, :string
    add_column :jobs, :required_language, :string
    add_column :jobs, :required_environment, :string
    add_column :jobs, :scripts, :string
    add_column :jobs, :success, :string
    add_column :jobs, :running, :string
    add_column :jobs, :repo, :string
    add_column :jobs, :commit, :string
  end
end
