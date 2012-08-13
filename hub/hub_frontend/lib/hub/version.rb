module Hub
  module VERSION #:nodoc:
    MAJOR = 0
    MINOR = 1
    TINY = 1
    BRANCH = 'devel'
    REVISION = nil 
    ARRAY    = [MAJOR, MINOR, TINY, BRANCH, REVISION].compact
    STRING   = ARRAY.join('.')

    def self.to_a; ARRAY  end
    def self.to_s; STRING end

  end
end
