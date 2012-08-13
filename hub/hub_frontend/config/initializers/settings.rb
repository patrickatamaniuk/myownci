#
# global settings and defines
#

#name of the exchange for ipc broadcasts
Rpcserver::Application.config.broadcast_exchange_name = 'myownci.broadcast'
#name of the dedicatet queue for commit events from repositories
Rpcserver::Application.config.commit_queue_name = 'myownci.git.commit'

# interval to check for pending jobs
Rpcserver::Application.config.jobs_check_interval = 30

