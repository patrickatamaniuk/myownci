class AddPlatformToMetal < ActiveRecord::Migration
  def change
    add_column :metals, :platform, :text
  end
end
