require 'hub/matrix'

describe Hub::Matrix do
  it "should be able to multiply a travis matrix" do
    config = {
        'language' => 'ruby'
    }
    Hub::Matrix.multiply(config){|job_arguments|
      puts "#{job_arguments}"
    }
  end
end
