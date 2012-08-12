class AddStateToRequests < ActiveRecord::Migration
  def change
    add_column :requests, :state, :string, :default => 'new', :null => false
  end
end
