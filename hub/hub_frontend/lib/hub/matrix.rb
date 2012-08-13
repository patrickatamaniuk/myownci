#see http://about.travis-ci.org/docs/user/build-configuration/
#unsupported: notifications, include, gemfile
#only ruby and python are supported languages
#extension: os specifies required build host operating system

module Hub
  class Matrix
    def self.multiply(request, cfg, &block)
      operatingsystem = cfg['os'] || ['Ubuntu 12.04']
      case cfg['language']
      when 'ruby'
        interpreters = cfg['rvm'] || "1.9.3"
        interpreter_key = 'rvm'
      when 'python'
        interpreters = cfg['python'] || "2.7"
        interpreter_key = 'python'
      else
        raise ArgumentError, "invalid language: #{cfg['language']}"
      end

      environments = cfg['env'] || [""]

      allow_failures = cfg['matrix']['allow_failures']
      exclude = cfg['matrix']['exclude']
      #includes = cfg['matrix']['include'] #not supported yet

      operatingsystem.each{|os|
        interpreters.each{|interpreter|
          environments.each{|environment|
            data = {'os'=>os, interpreter_key=>interpreter, 'env'=>environment}
            next if self.matrix_match exclude, data
            failure_allowed = self.matrix_match allow_failures, data

            attributes = {
              :script => cfg['script'],
              :before_script => cfg['before_script'],
              :after_script => cfg['after_script'],
              :install => cfg['install'],
              :before_install => cfg['before_install'],
              :after_install => cfg['after_install'],
              :operating_system => os,
              :language => cfg['language'],
              :interpreter => interpreter,
              :environment => environment,
              :failure_allowed => failure_allowed
            }
            yield attributes
          }
        }
      }
   
    end

    def self.matrix_match(exclude, data)
      exclude.each{|exclude_term|
        match = true
        exclude_term.each{|key, val|
          if val != data[key]
            match = false
          end
        }
        return true if match
      }
      return false
    end

  end
end
