import matplotlib.pyplot as plt
import matplotlib.animation as ani
import numpy as np

# RGB tuples to represent colors to encode health status
GREY = (0.78, 0.78, 0.78)   # uninfected
RED = (0.96, 0.15, 0.15)    # infected
GREEN = (0, 0.86, 0.03)     # recovered
BLACK = (0, 0, 0)           # dead
