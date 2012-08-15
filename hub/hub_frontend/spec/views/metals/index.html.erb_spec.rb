require 'spec_helper'

describe "metals/index" do
  before(:each) do
    assign(:metals, [
      stub_model(Metal,
        :name => "Name",
        :uuid => "Uuid",
        :state => "State"
      ),
      stub_model(Metal,
        :name => "Name",
        :uuid => "Uuid",
        :state => "State"
      )
    ])
  end

  it "renders a list of metals" do
    render
    # Run the generator again with the --webrat flag if you want to use webrat matchers
    assert_select "tr>td", :text => "Name".to_s, :count => 2
    assert_select "tr>td", :text => "Uuid".to_s, :count => 2
    assert_select "tr>td", :text => "State".to_s, :count => 2
  end
end
