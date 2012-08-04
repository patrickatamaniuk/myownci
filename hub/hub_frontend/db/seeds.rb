# This file should contain all the record creation needed to seed the database with its default values.
# The data can then be loaded with the rake db:seed (or created alongside the db with db:setup).
#
superrole = Role.create!()
superrole.name = 'superadmin'
superrole.save!
adminrole = Role.create!()
adminrole.name = 'admin'
adminrole.save!
workerrole = Role.create!()
workerrole.name = 'worker'
workerrole.save!
user = User.create!(email: 'admin@localhost.com', password: 'defaultadminpassword', password_confirmation: 'defaultadminpassword')
user.name = 'admin'
user.roles = [ adminrole, superrole ]
user.save!
worker = User.create!(email: 'worker1@localhost.com', password: 'defaultadminpassword', password_confirmation: 'defaultadminpassword')
worker.name = 'worker1'
worker.roles = [ workerrole ]
worker.reset_authentication_token!
worker.save!
