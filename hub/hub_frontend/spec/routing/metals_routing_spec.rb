require "spec_helper"

describe MetalsController do
  describe "routing" do

    it "routes to #index" do
      get("/metals").should route_to("metals#index")
    end

    it "routes to #new" do
      get("/metals/new").should route_to("metals#new")
    end

    it "routes to #show" do
      get("/metals/1").should route_to("metals#show", :id => "1")
    end

    it "routes to #edit" do
      get("/metals/1/edit").should route_to("metals#edit", :id => "1")
    end

    it "routes to #create" do
      post("/metals").should route_to("metals#create")
    end

    it "routes to #update" do
      put("/metals/1").should route_to("metals#update", :id => "1")
    end

    it "routes to #destroy" do
      delete("/metals/1").should route_to("metals#destroy", :id => "1")
    end

  end
end
