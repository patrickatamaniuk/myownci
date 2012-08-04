class CreateWorkers < ActiveRecord::Migration
  def change
    create_table :workers do |t|
      t.string :name
      t.string :ip
      t.string :vmimage
      t.string :vmname
      t.string :snapshottag

      t.timestamps
    end
  end
end
