require 'spec_helper'

describe "metals/show" do
  before(:each) do
    @metal = assign(:metal, stub_model(Metal,
      :name => "Name",
      :uuid => "Uuid",
      :state => "State"
    ))
  end

  it "renders attributes in <p>" do
    render
    # Run the generator again with the --webrat flag if you want to use webrat matchers
    rendered.should match(/Name/)
    rendered.should match(/Uuid/)
    rendered.should match(/State/)
  end
end
