import numpy as np

import globals
import settlementTools
from settlement.DebugSettlement import DebugSettlement

globals.initialize()

# TODO create settlement class
#   - objective function
#   - structure sets


globalRNG = np.random.default_rng(847283947239819292)

# START generator

DebugSettlement(rng=globalRNG)

# END generator

settlementTools.placeNodes()
