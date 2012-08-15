require 'spec_helper'
require 'json'

# Specs in this file have access to a helper object that includes
# the MetalsHelper. For example:
#

eventdata = %Q|{"workers": [{"nodename": "precise-ci", "exeformat": "ELF", "system": "Linux", "capabilities": ["ruby python"], "architecture": "64bit", "distribution": ["Ubuntu", "12.04", "precise"], "processor": "x86_64", "uuid": "f7bf4899-6b87-4ef0-b704-a12c455b718b"}], "envelope": {"hostname": "videohorst", "uuid": "b6de1cfa-a844-45b3-91c0-3a3cb21be638"}}|

 describe MetalsHelper do
   describe "react on amqp event" do
     it "creates a metal from amqp event" do
       data = JSON.load(eventdata)
       helper.create_from_push(data)

       Metal.find(:all).length.should eq 1
       metal = Metal.find(:all).first
       metal.should_not be nil
       metal.should_not be nil
       metal.name.should eq 'videohorst'
       metal.workers.should_not be nil
       metal.workers.length.should eq 1
       metal.workers[0].name.should eq 'precise-ci'
     end

     it "updates a metal from amqp event" do
       data = JSON.load(eventdata)
       helper.create_from_push(data)
       data = JSON.load(eventdata)
       helper.create_from_push(data)
       Metal.find(:all).length.should eq 1
     end
   end
 end
