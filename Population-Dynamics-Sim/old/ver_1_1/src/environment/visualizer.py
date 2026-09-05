import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np


class Visualizer:
    def __init__(self):
        """Simple 3D visualizer for organisms.

        Args:
            bounds: Size of the visualization space (default: 10)
        """
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.bounds = bounds
        self.ax.set_xlim(0, bounds)
        self.ax.set_ylim(0, bounds)
        self.ax.set_zlim(0, bounds)

    def update(self, positions):
        """Update organism positions.

        Args:
            positions: List of [x, y, z] coordinates, e.g. [[1, 2, 3], [4, 5, 6]]
        """
        
        # clears board
        self.ax.clear()
        
        # re-sets the boundaries of the 3d space
        ## If this is removed, the previous states stay creating copies of the dots
        self.ax.set_xlim(0, self.bounds)
        print("self.ax.set_xlim",self.ax)
        self.ax.set_ylim(0, self.bounds)
        print("self.ax.set_ylim", self.ax)
        self.ax.set_zlim(0, self.bounds)
        print("self.ax.set_zlim", self.ax)
        
        positions = np.array(positions)
        print("positions", positions)
        self.ax.scatter(positions[:, 0], positions[:, 1], positions[:, 2], s=100)
        print("self.ax.scatter(positions[:,0], positions[:,1], etc...)", self.ax)
