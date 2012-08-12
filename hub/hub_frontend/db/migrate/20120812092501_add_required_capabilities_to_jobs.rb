class AddRequiredCapabilitiesToJobs < ActiveRecord::Migration
  def change
    add_column :jobs, :scripts, :text
    add_column :jobs, :required_os, :string
    add_column :jobs, :required_language, :string
    add_column :jobs, :required_environment, :string
  end
end
