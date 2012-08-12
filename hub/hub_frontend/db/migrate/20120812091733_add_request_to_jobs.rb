class AddRequestToJobs < ActiveRecord::Migration
  def change
    add_column :jobs, :request_id, :integer
    add_index :jobs, :request_id
  end
end
