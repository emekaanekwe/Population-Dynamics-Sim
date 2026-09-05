from matplotlib.animation import FuncAnimation
import numpy as np
'''

Each molecule type has inherent properties:

Reactivity (which other molecules it can react with)
Diffusion rate
Stability (decay rate)
Energy content
'''

class Agent:
    def __init__(self):
        self.start_point = []
        self.reactivity = []
        self.diffusion_rate = 0
        self.decay_rate = 0
        self.positions = np.random.uniform(0, 10)
        
        
                
    def stating_position(self):
        print("sets starting position")
        
    def move(self, direction):
        pos_x, pos_y = direction
        self.start_point[0] = pos_x + self.start_point[0] #should possibly be 2D array 
        self.start_point[0] = pos_y + self.start_point[0]
        
