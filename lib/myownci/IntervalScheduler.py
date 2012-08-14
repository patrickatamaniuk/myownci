class IntervalScheduler:

    def __init__(self, connection, callback=None, interval=10):
        self._connection = connection
        self._callback = callback
        self._interval = interval
        self._start_timer()

    def _start_timer(self):
        self._connection.add_timeout(self._interval, self.tick)

    def tick(self):
        self._start_timer()
        if self._callback:
            self._callback()


