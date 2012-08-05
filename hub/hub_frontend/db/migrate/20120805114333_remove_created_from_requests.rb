class RemoveCreatedFromRequests < ActiveRecord::Migration
  def up
    remove_column :requests, :created
  end

  def down
    add_column :requests, :created, :datetime
  end
end
