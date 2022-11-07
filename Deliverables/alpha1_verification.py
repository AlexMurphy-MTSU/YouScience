import pandas as pd
import numpy as np
from collections import Counter

# implementing random seed for control
sd = 42
np.random.seed(sd)

# school names for consistency 
schools = ['Oakland Middle School',
    'Siegel Middle School',
    'Whitworth-Buchanan Middle School',
    'Christiana Middle School',
    'Smyrna Middle School',
    'Stewarts Creek Middle School',
    'Rockvale Middle School',
    'Rocky Fork Middle School',
    'Blackman Middle School',
    'Thurman Francis Arts Academy',
    'Rock Springs Middle School',
    'LaVergne Middle School'
]

# Priority: verify that every student on a school's skyward roster has a schedule
