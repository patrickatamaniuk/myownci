class CreateJobs < ActiveRecord::Migration
  def change
    create_table :jobs do |t|
      t.string :repo
      t.string :commit
      t.datetime :started
      t.datetime :finished
      t.references :worker
      t.boolean :running
      t.boolean :success

      t.timestamps
    end
    add_index :jobs, :worker_id
  end
end
