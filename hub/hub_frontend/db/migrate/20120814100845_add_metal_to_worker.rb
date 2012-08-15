class AddMetalToWorker < ActiveRecord::Migration
  def change
    add_column :workers, :metal_id, :int
    add_column :workers, :uuid, :string
    add_column :workers, :last_seen_at, :datetime
    add_column :workers, :state, :string
  end
end
