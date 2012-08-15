require 'spec_helper'
require 'json'

# Specs in this file have access to a helper object that includes
# the MetalsHelper. For example:
#

#eventdata = %Q|{"workers": [{"var": {"identity": {"hwaddrlist": ["00:50:56:00:11:02", "52:54:00:5a:79:02"], "processor": "x86_64", "nodename": "precise-ci", "exeformat": "ELF", "distribution": ["Ubuntu", "12.04", "precise"], "system": "Linux", "architecture": "64bit"}}, "worker-info": [{"capabilities": ["ruby", "python"]}], "hostname": "precise-ci", "host-uuid": "f7bf4899-6b87-4ef0-b704-a12c455b718b"}], "envelope": {"hostname": "videohorst", "uuid": "b6de1cfa-a844-45b3-91c0-3a3cb21be638"}}|

eventdata = %Q|{"workers": [{"uuid": "f7bf4899-6b87-4ef0-b704-a12c455b718b", "processor": "x86_64", "nodename": "precise-ci", "exeformat": "ELF", "distribution": ["Ubuntu", "12.04", "precise"], "system": "Linux", "architecture": "64bit"}], "envelope": {"hostname": "videohorst", "uuid": "b6de1cfa-a844-45b3-91c0-3a3cb21be638"}}|

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
