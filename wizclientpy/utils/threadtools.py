from threading import Thread, Event


class IntervalTimer(Thread):
    def __init__(self, interval, function, args=None, kwargs=None):
        # To prevent the timer from blocking the program, set daemon=True.
        Thread.__init__(self, daemon=False)
        self.interval = interval
        self.function = function
        self.args = args if args is not None else []
        self.kwargs = kwargs if kwargs is not None else {}
        self.finished = Event()

    def cancel(self):
        """Stop the interval timer."""
        self.finished.set()

    def run(self):
        # If `finished` event was set to true before waiting,
        # the loop will exit.
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)
