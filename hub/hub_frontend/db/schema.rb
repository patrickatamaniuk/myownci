# encoding: UTF-8
# This file is auto-generated from the current state of the database. Instead
# of editing this file, please use the migrations feature of Active Record to
# incrementally modify your database, and then regenerate this schema definition.
#
# Note that this schema.rb definition is the authoritative source for your
# database schema. If you need to create the application database on another
# system, you should be using db:schema:load, not running all the migrations
# from scratch. The latter is a flawed and unsustainable approach (the more migrations
# you'll amass, the slower it'll run and the greater likelihood for issues).
#
# It's strongly recommended to check this file into your version control system.

ActiveRecord::Schema.define(:version => 20120805114333) do

  create_table "jobs", :force => true do |t|
    t.string   "repo"
    t.string   "commit"
    t.datetime "started"
    t.datetime "finished"
    t.integer  "worker_id"
    t.boolean  "running"
    t.boolean  "success"
    t.datetime "created_at", :null => false
    t.datetime "updated_at", :null => false
  end

  add_index "jobs", ["worker_id"], :name => "index_jobs_on_worker_id"

  create_table "requests", :force => true do |t|
    t.string   "repo"
    t.string   "commit"
    t.datetime "created_at",      :null => false
    t.datetime "updated_at",      :null => false
    t.text     "buildconfig"
    t.text     "commits"
    t.string   "ref"
    t.string   "author_name"
    t.string   "author_email"
    t.string   "committer_name"
    t.string   "committer_email"
    t.datetime "committed_date"
  end

  create_table "roles", :force => true do |t|
    t.string   "name"
    t.datetime "created_at", :null => false
    t.datetime "updated_at", :null => false
  end

  create_table "roles_users", :id => false, :force => true do |t|
    t.integer "role_id"
    t.integer "user_id"
  end

  create_table "users", :force => true do |t|
    t.string   "email",                  :default => "",    :null => false
    t.string   "encrypted_password",     :default => "",    :null => false
    t.string   "reset_password_token"
    t.datetime "reset_password_sent_at"
    t.datetime "remember_created_at"
    t.integer  "sign_in_count",          :default => 0
    t.datetime "current_sign_in_at"
    t.datetime "last_sign_in_at"
    t.string   "current_sign_in_ip"
    t.string   "last_sign_in_ip"
    t.string   "authentication_token"
    t.datetime "created_at",                                :null => false
    t.datetime "updated_at",                                :null => false
    t.boolean  "admin",                  :default => false
    t.string   "name"
    t.string   "first_name"
    t.string   "last_name"
  end

  add_index "users", ["authentication_token"], :name => "index_users_on_authentication_token", :unique => true
  add_index "users", ["email"], :name => "index_users_on_email", :unique => true
  add_index "users", ["reset_password_token"], :name => "index_users_on_reset_password_token", :unique => true

  create_table "workers", :force => true do |t|
    t.string   "name"
    t.string   "ip"
    t.string   "vmimage"
    t.string   "vmname"
    t.string   "snapshottag"
    t.datetime "created_at",  :null => false
    t.datetime "updated_at",  :null => false
  end

end
