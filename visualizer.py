import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.lines import Line2D
import numpy as np

class Visualizer:
    @staticmethod
    def draw_pitch(ax, pitch_length=105, pitch_width=68):
        """
        Draws a realistic football pitch on the given Matplotlib axis.
        Includes grass stripes, goals, arcs, and accurate markings.
        """
        # Set background (Grass color)
        # We will draw stripes instead of a single facecolor
        ax.set_facecolor('#4B823B') # Base green

        # Dimensions assuming Center is (0,0)
        half_len = pitch_length / 2.0
        half_width = pitch_width / 2.0
        
        # Draw Grass Stripes (Vertical)
        n_stripes = 13 # Commonly used number
        stripe_width = pitch_length / n_stripes
        for i in range(n_stripes):
            if i % 2 == 0:
                color = '#4B823B' # Darker
            else:
                color = '#5C944D' # Lighter
            
            # X start
            x0 = -half_len + i * stripe_width
            rect = patches.Rectangle((x0, -half_width - 5), stripe_width, pitch_width + 10, 
                                     linewidth=0, facecolor=color, zorder=0)
            ax.add_patch(rect)

        # Line Properties
        lc = 'white' # Line color
        lw = 2 # Line width
        
        # Perimeter
        ax.plot([-half_len, half_len], [-half_width, -half_width], color=lc, linewidth=lw, zorder=1)
        ax.plot([-half_len, half_len], [half_width, half_width], color=lc, linewidth=lw, zorder=1)
        ax.plot([-half_len, -half_len], [-half_width, half_width], color=lc, linewidth=lw, zorder=1)
        ax.plot([half_len, half_len], [-half_width, half_width], color=lc, linewidth=lw, zorder=1)
        
        # Halfway line
        ax.plot([0, 0], [-half_width, half_width], color=lc, linewidth=lw, zorder=1)
        
        # Center circle
        center_circle = patches.Circle((0, 0), 9.15, edgecolor=lc, facecolor='none', linewidth=lw, zorder=1)
        ax.add_patch(center_circle)
        centre_spot = patches.Circle((0, 0), 0.6, facecolor=lc, zorder=1)
        ax.add_patch(centre_spot)
        
        # Penalty & Goal Dimensions
        pen_len = 16.5
        pen_width = 40.32
        pen_width_half = pen_width / 2
        
        goal_len = 5.5
        goal_width = 18.32
        goal_width_half = goal_width / 2
        
        # Penalty Areas
        # Left
        ax.plot([-half_len, -half_len + pen_len], [pen_width_half, pen_width_half], color=lc, linewidth=lw, zorder=1)
        ax.plot([-half_len, -half_len + pen_len], [-pen_width_half, -pen_width_half], color=lc, linewidth=lw, zorder=1)
        ax.plot([-half_len + pen_len, -half_len + pen_len], [-pen_width_half, pen_width_half], color=lc, linewidth=lw, zorder=1)
        # Right
        ax.plot([half_len, half_len - pen_len], [pen_width_half, pen_width_half], color=lc, linewidth=lw, zorder=1)
        ax.plot([half_len, half_len - pen_len], [-pen_width_half, -pen_width_half], color=lc, linewidth=lw, zorder=1)
        ax.plot([half_len - pen_len, half_len - pen_len], [-pen_width_half, pen_width_half], color=lc, linewidth=lw, zorder=1)
        
        # Goal Areas (6-yard box)
        # Left
        ax.plot([-half_len, -half_len + goal_len], [goal_width_half, goal_width_half], color=lc, linewidth=lw, zorder=1)
        ax.plot([-half_len, -half_len + goal_len], [-goal_width_half, -goal_width_half], color=lc, linewidth=lw, zorder=1)
        ax.plot([-half_len + goal_len, -half_len + goal_len], [-goal_width_half, goal_width_half], color=lc, linewidth=lw, zorder=1)
        # Right
        ax.plot([half_len, half_len - goal_len], [goal_width_half, goal_width_half], color=lc, linewidth=lw, zorder=1)
        ax.plot([half_len, half_len - goal_len], [-goal_width_half, -goal_width_half], color=lc, linewidth=lw, zorder=1)
        ax.plot([half_len - goal_len, half_len - goal_len], [-goal_width_half, goal_width_half], color=lc, linewidth=lw, zorder=1)
        
        # Penalty Spots
        pen_spot_dist = 11.0
        ax.add_patch(patches.Circle((-half_len + pen_spot_dist, 0), 0.6, facecolor=lc, zorder=1))
        ax.add_patch(patches.Circle((half_len - pen_spot_dist, 0), 0.6, facecolor=lc, zorder=1))

        # Penalty Arcs
        # Basic implementation using Arc
        # Left
        arc_l = patches.Arc((-half_len + pen_spot_dist, 0), 18.3, 18.3, theta1=-53, theta2=53, edgecolor=lc, linewidth=lw, zorder=1)
        ax.add_patch(arc_l)
        # Right
        arc_r = patches.Arc((half_len - pen_spot_dist, 0), 18.3, 18.3, theta1=127, theta2=233, edgecolor=lc, linewidth=lw, zorder=1)
        ax.add_patch(arc_r)
        
        # Goals (Actual nets outside pitch)
        goal_depth = 2.44
        goal_opening = 7.32
        # Left Goal
        ax.add_patch(patches.Rectangle((-half_len - goal_depth, -goal_opening/2), goal_depth, goal_opening, 
                     facecolor='none', edgecolor=lc, linewidth=lw, alpha=0.5, zorder=1))
        # Right Goal
        ax.add_patch(patches.Rectangle((half_len, -goal_opening/2), goal_depth, goal_opening, 
                     facecolor='none', edgecolor=lc, linewidth=lw, alpha=0.5, zorder=1))

        # Config axis
        # Slightly larger view than pitch
        ax.set_xlim(-half_len - 5, half_len + 5)
        ax.set_ylim(-half_width - 5, half_width + 5)
        ax.set_aspect('equal')
        ax.axis('off')
        
        # Remove margins
        ax.set_position([0, 0, 1, 1])

    @staticmethod
    def plot_chain(ax, coords, color='blue', label=None, linestyle='-', marker='o', alpha=1.0):
        if not coords:
            return
        
        xs = [p[0] for p in coords]
        ys = [p[1] for p in coords]
        
        # Plot path
        ax.plot(xs, ys, color=color, linestyle=linestyle, linewidth=2, label=label, zorder=2, alpha=alpha)
        # Plot start
        ax.scatter(xs[0], ys[0], color='white', edgecolor=color, s=100, marker='o', zorder=3, alpha=alpha)
        # Plot rest
        ax.scatter(xs[1:], ys[1:], color=color, s=50, marker=marker, zorder=3, alpha=alpha)
        # Arrows for direction?
        for i in range(len(xs) - 1):
            ax.annotate('', xy=(xs[i+1], ys[i+1]), xytext=(xs[i], ys[i]),
                        arrowprops=dict(arrowstyle='->', color=color, lw=1.5, alpha=alpha), zorder=2)
