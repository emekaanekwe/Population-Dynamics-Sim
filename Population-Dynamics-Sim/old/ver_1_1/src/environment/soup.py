'''
Need to have enviro mutate like agents do
'''
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np

'''generate environment for organisms to exist in'''
class Soup:
    def __init__(self, bounds=10):    
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.bounds = bounds
        self.ax.set_xlim(0, bounds)
        self.ax.set_ylim(0, bounds)
        self.ax.set_zlim(0, bounds)

    def animate(self, position_frames, fps=30, filename='animation.mp4'):
        def update_frame(frame_num):
                self.update_positions(position_frames[frame_num])
        anim = FuncAnimation(self.fig, update_frame, frames=len(position_frames), interval=1000/fps)
        anim.save(filename, writer='ffmpeg', fps=fps)
        plt.close()

    
    def update_positions(self, positions):
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
    
    #def init_agents(self, agent_list):        
        # positions of agents
        #print("positions", agent_list)
        
        # sets agents in a random position 
        #self.ax.scatter(agent_list[:, 0], agent_list[:, 1], agent_list[:, 2], s=100)
        self.ax.scatter(positions[:, 0], positions[:, 1], positions[:, 2], s=100)
        print("self.ax.scatter(positions[:,0], positions[:,1], etc...)", self.ax)
    