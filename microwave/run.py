import sys
import importlib.util
import atexit

import tkinter
from tkinter.constants import BOTH, NO
from lib import gui, simulator
from lib.test import print_trace

def my_import(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

def run_demo(model_module, time_scale):
    input_trace = []
    output_trace = []

    sc = model_module.Statechart()
    controller = simulator.Controller()
    sc.timer_service = simulator.TimerService(controller, time_scale)

    tk = tkinter.Tk()
    tk.withdraw()
    toplevel = tkinter.Toplevel(tk)
    toplevel.resizable(width=NO, height=NO)
    toplevel.title("Microwave oven simulator")
    g = gui.GUI(toplevel)

    def on_update():
        pass

    sim = simulator.RealTimeSimulation(controller, toplevel, on_update)

    def send_event(event: str):
        timestamp = sim.add_input(sc, event)
        input_trace.append((timestamp, event, None))

    g.send_event = send_event

    class MyObserver():
        def __init__(self, event):
            self.event = event

        def next(self, value=None):
            print("Time = %03dms - Output event: %s" % (controller.get_simtime_seconds()*1000, self.event))
            g.handle_event(self.event, value)
            output_trace.append((controller.simulated_time, self.event, value))

    sc.turn_magnetron_on_observable.subscribe(MyObserver("turn_magnetron_on"))
    sc.turn_magnetron_off_observable.subscribe(MyObserver("turn_magnetron_off"))
    sc.set_displayed_time_observable.subscribe(MyObserver("set_displayed_time"))
    sc.ring_bell_observable.subscribe(MyObserver("ring_bell"))

    def print_exit_trace():
        print("Exiting...")
        print("Full trace (you can add this to the SCENARIOS in test.py)...")
        print("{")
        print("    \"name\": \"interactive\",")
        print("    \"input_trace\": ", end='')
        print_trace(input_trace, 4)
        print(",")
        print("    \"output_trace\": ", end='')
        print_trace(output_trace, 4)
        print(",")
        print("}")

    atexit.register(print_exit_trace)

    controller.start()
    sc.enter()
    sim.interrupt() # schedule first wakeup
    tk.mainloop()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python run.py MODELNAME [TIME_SCALE]")
        print("")
        print("Example:")
        print("  python run.py 50_History 2.0")
        sys.exit(1)

    model_name = sys.argv[1]
    if len(sys.argv) == 3:
       time_scale = float(sys.argv[2])
    else:
       time_scale = 1.0

    model_module = my_import("sc", "YAKINDU_WORKSPACE/" + model_name + "/srcgen/statechart.py")
    run_demo(model_module, time_scale)
