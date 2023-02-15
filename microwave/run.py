import sys
import importlib.util

import tkinter
from tkinter.constants import BOTH, NO
from lib import gui, simulator

def my_import(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

def run_demo(model_module, time_scale):
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
        sim.add_input(sc, event)

    g.send_event = send_event

    class MyObserver():
        def __init__(self, event):
            self.event = event

        def next(self, value=None):
            print("Time = %03dms - Output event: %s" % (controller.get_simtime_seconds()*1000, self.event))
            g.handle_event(self.event, value)

    sc.turn_magnetron_on_observable.subscribe(MyObserver("turnMagnetronOn"))
    sc.turn_magnetron_off_observable.subscribe(MyObserver("turnMagnetronOff"))
    sc.set_displayed_time_observable.subscribe(MyObserver("setDisplayedTime"))
    sc.ring_bell_observable.subscribe(MyObserver("ringBell"))

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
        print("  python run.py 50_ChildLock 2.0")
        sys.exit(1)

    model_name = sys.argv[1]
    if len(sys.argv) == 3:
       time_scale = float(sys.argv[2])
    else:
       time_scale = 1.0

    model_module = my_import("sc", "YAKINDU_WORKSPACE/" + model_name + "/srcgen/statechart.py")
    run_demo(model_module, time_scale)
