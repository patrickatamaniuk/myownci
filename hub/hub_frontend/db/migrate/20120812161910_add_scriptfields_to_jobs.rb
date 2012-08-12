class AddScriptfieldsToJobs < ActiveRecord::Migration
  def change
    add_column :jobs, :before_install, :text
    add_column :jobs, :install, :text
    add_column :jobs, :after_install, :text
    add_column :jobs, :before_script, :text
    add_column :jobs, :script, :text
    add_column :jobs, :after_script, :text
    add_column :jobs, :language, :string
    add_column :jobs, :interpreter, :string
    add_column :jobs, :environment, :string
    add_column :jobs, :operating_system, :string
    add_column :jobs, :failure_allowed, :boolean
    add_column :jobs, :started_at, :datetime
    add_column :jobs, :finished_at, :datetime
  end
end
