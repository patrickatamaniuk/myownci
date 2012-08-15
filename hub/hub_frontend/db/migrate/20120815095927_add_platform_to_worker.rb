class AddPlatformToWorker < ActiveRecord::Migration
  def change
    add_column :workers, :platform, :text
  end
end
