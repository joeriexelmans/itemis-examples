import sys
import importlib.util

import tkinter
from tkinter.constants import BOTH, NO
from lib import gui, simulator
from lib import test as testing_framework
from run import my_import

SCENARIOS = [
{
    "name": "magnetron shuts off when door opened",
    "input_trace": [
        (1739451957, "start_pressed", None),
        (4262358465, "door_opened", None),
    ],
    "output_trace": [
        # start button was pressed, setting timer to 10 and starting the microwave
        (1739451957, "set_displayed_time", 10),
        (1739451957, "turn_magnetron_on", None),
        # timer counts down:
        (2739451957, "set_displayed_time", 9),
        (3739451957, "set_displayed_time", 8),
        # door is opened:
        (4262358465, "turn_magnetron_off", None),
    ],
},
]

IDEMPOTENT = [
    "turn_magnetron_on",
    "turn_magnetron_off",
    "set_display_time",
]

INITIAL = [
    ("turn_magnetron_off", None),
    ("set_display_time", 0),
]

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage:")
        print("  python test.py MODELNAME")
        print("")
        print("Example:")
        print("  python test.py 50_History")
        sys.exit(1)

    model_name = sys.argv[1]

    model_module = my_import("sc", "YAKINDU_WORKSPACE/" + model_name + "/srcgen/statechart.py")
    # run_test(model_module)

    for scenario in SCENARIOS:
        print("Running scenario:", scenario["name"])
        testing_framework.run_test(scenario["input_trace"],
            scenario["output_trace"],
            model_module.Statechart,
            INITIAL,
            IDEMPOTENT,
            verbose=False)
