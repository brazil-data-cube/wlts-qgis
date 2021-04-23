"""WLTS Python Client Examples."""


import matplotlib.pyplot as plt
import numpy as np
from wlts import WLTS

# Change to the WLTS URL you want to use.
service = WLTS('https://brazildatacube.dpi.inpe.br/wlts')

# Example of trajectory operation
tj = service.tj(
    latitude=-6.37, longitude=-57.13,
    collections='terraclass_amazonia,deter_amazonia_legal', geometry=False,
    start_date='1999-01-01', end_date='2021-01-01'
)

print(tj.trajectory)