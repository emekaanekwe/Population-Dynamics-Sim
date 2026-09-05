# run the program
from ver_1_1.src.environment.soup  import Soup
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np

# hyperparams
organisms = 3
steps = 20
frames = []


if __name__ == "__main__":
    soup = Soup(bounds=10)
    for step in range(steps):
    # Move organisms randomly (small random walk)
        positions += np.random.uniform(-0.2, 0.2, size=(organisms, 3))
        print("random move", positions)
        # Keep organisms in bounds
        #positions = np.clip(positions, 0, viz.bounds)
        #print("positions clip", positions)
        # Store this frame
        frames.append(positions.copy())
        

    # Create animation
    soup.animate(frames, fps=30)
    soup.update_positions(positions)
    print("===Animation saved as animation.mp4===")

    """static display of environment
    def show():
        plt.show()
    """