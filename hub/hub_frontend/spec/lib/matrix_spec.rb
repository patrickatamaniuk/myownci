require 'yaml'
require 'hub/matrix'

describe Hub::Matrix do
@data = [
    {:count => 1, :yml => %Q|
    language: ruby
    |},

    {:count => 1, :yml => %Q|
    language: python
    |},

    {:count => 3, :yml => %Q|
    language: ruby
    rvm:
    - "1.9.3"
    - "1.8.7"
    env:
    - "e1"
    - "e2"
    matrix:
      exclude:
      - env: e1
        rvm: "1.8.7"
    |}
]

  index = 1
  @data.each{|data|
  config = YAML.load(data[:yml])
  count = data[:count]
  it "should be able to multiply a simple matrix" do
    result = []
    Hub::Matrix.multiply(config){|job_arguments|
      result << job_arguments
    }
    result.length.should == count
    index = index + 1
  end
  }
end
