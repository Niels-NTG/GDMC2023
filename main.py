import numpy as np

import globals
import settlementTools
from settlement.FaunaObservationPost import FaunaObservationPost

globals.initialize()


globalRNG = np.random.default_rng()

# START generator

FaunaObservationPost(rng=globalRNG)

# END generator

settlementTools.placeNodes()
