import logging
def mlog(*args):
  logging.info(u' '.join(["%s"%a for a in args]))

