# Author: Joeri Exelmans

import time

class QueueEntry:
    # Make the common case fast:
    __slots__ = ('timestamp', 'callback', 'canceled', 'debug')

    def __init__(self, timestamp, callback, debug):
        self.timestamp = timestamp
        self.callback = callback
        self.canceled = False
        self.debug = debug

# Simulation primitive.
# Uses virtualized (simulated) time, instead of looking at the wall clock.
class Controller:
    def __init__(self):
        self.event_queue = []
        self.simulated_time = 0

    def start(self):
        now = time.perf_counter_ns()
        self.simulated_time = now
        self.start_time = now

    def add_input(self, timestamp, sc, event, value=None):
        raise_method = getattr(sc, 'raise_' + event)
        if value is not None:
            callback = lambda: raise_method(value)
        else:
            callback = raise_method
        self.add_input_lowlevel(timestamp, callback, event)

    def add_input_lowlevel(self, timestamp, callback, debug):
        e = QueueEntry(timestamp, callback, debug)
        self.event_queue.append(e)
        self.event_queue.sort(key = lambda entry: entry.timestamp, reverse=True)
        return e

    def run_until(self, until):
        while self.have_event() and self.get_earliest() <= until:
            e = self.event_queue.pop();
            if not e.canceled:
                self.simulated_time = e.timestamp
                print("Time = %03dms - Input event: %s" % (self.get_simtime_seconds()*1000, e.debug))
                e.callback()

    def have_event(self):
        return len(self.event_queue) > 0

    def get_earliest(self):
        return self.event_queue[-1].timestamp

    def get_simtime_seconds(self):
        return (self.simulated_time - self.start_time) / 1000000000

# Our own timer service, used by the statechart.
# Much better than YAKINDU's pathetic timer service.
class TimerService:
    def __init__(self, controller, scale=1.0):
        self.controller = controller;
        self.timers = {}
        self.scale = scale

    # Duration: milliseconds
    def set_timer(self, sc, event_id, duration, periodic):
        def callback():
            sc.time_elapsed(event_id)

        self.unset_timer(callback, event_id)

        controller_duration = duration * 1000000 / self.scale # ms to ns

        e = self.controller.add_input_lowlevel(
            self.controller.simulated_time + controller_duration, # timestamp relative to simulated time
            callback,
            "timer"+str(event_id))

        self.timers[event_id] = e

    def unset_timer(self, callback, event_id):
        try:
            e = self.timers[event_id]
            e.canceled = True
        except KeyError:
            pass

# Runs the Controller as close as possible to the wall-clock.
# Depending on how fast your computer is, simulated time will always run a tiny bit behind wall-clock time, but this error will NOT grow over time.
class RealTimeSimulation:
    def __init__(self, controller, tk, update_callback):
        self.controller = controller
        self.tk = tk
        self.update_callback = update_callback

        self.scheduled_id = None
        self.purposefully_behind = 0

    def add_input(self, sc, event, value=None):
        now = time.perf_counter_ns() + self.purposefully_behind
        self.controller.add_input(now, sc, event, value)
        self.interrupt()

    def interrupt(self):
        if self.scheduled_id is not None:
            self.tk.after_cancel(self.scheduled_id)

        if self.controller.have_event():
            now = time.perf_counter_ns()
            earliest = self.controller.get_earliest()
            sleep_time = earliest - now

            if sleep_time < 0:
                self.purposefully_behind = sleep_time
            else:
                self.purposefully_behind = 0

            def callback():
                self.controller.run_until(now + self.purposefully_behind)
                self.update_callback()
                self.interrupt()

            self.scheduled_id = self.tk.after(int(sleep_time / 1000000), callback)
        # else:
            # print("sleeping until next input")
