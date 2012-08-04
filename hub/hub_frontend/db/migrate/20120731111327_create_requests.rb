class CreateRequests < ActiveRecord::Migration
  def change
    create_table :requests do |t|
      t.string :repo
      t.string :commit
      t.datetime :created

      t.timestamps
    end
  end
end
