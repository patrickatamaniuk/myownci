class AddDetailsToRequests < ActiveRecord::Migration
  def change
    add_column :requests, :buildconfig, :text
    add_column :requests, :commits, :text
    add_column :requests, :ref, :string
    add_column :requests, :author_name, :string
    add_column :requests, :author_email, :string
    add_column :requests, :committer_name, :string
    add_column :requests, :committer_email, :string
    add_column :requests, :committed_date, :datetime
  end
end
