class AddStateToJobs < ActiveRecord::Migration
  def change
    add_column :jobs, :state, :string, :default => 'new', :null => false
  end
end
