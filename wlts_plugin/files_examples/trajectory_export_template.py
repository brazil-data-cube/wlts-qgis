import matplotlib.pyplot as plt
import numpy as np

#
"""WLTS Python Client Examples."""

from wlts import WLTS

# Change to the WLTS URL you want to use.
service = WLTS('{service_host}')

# Example of trajectory operation
tj = service.tj(latitude={latitude}, longitude={longitude}, collections='{collections}')

print(tj.trajectory)