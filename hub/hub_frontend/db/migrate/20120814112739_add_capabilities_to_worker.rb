class AddCapabilitiesToWorker < ActiveRecord::Migration
  def change
    add_column :workers, :system, :string
    add_column :workers, :architecture, :string
    add_column :workers, :distribution, :string
    add_column :workers, :capabilities, :string
  end
end
