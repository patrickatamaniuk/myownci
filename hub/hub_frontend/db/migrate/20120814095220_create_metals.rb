class CreateMetals < ActiveRecord::Migration
  def change
    create_table :metals do |t|
      t.string :name
      t.string :uuid
      t.datetime :last_seen_at
      t.string :state

      t.timestamps
    end
  end
end
