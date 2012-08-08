import sys
def mlog(*args):
  sys.stderr.write(u' '.join(["%s"%a for a in args]))
  sys.stderr.write(u'\n')
  sys.stderr.flush()

