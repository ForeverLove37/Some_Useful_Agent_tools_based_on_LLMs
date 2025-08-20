import matplotlib.pyplot as plt
import numpy as np

# This script demonstrates plotting four different mathematical functions.
# Each function will be in its own subplot.

# Generate some data
x = np.linspace(0, 2 * np.pi, 400)
y1 = np.sin(x)
y2 = np.cos(x)
y3 = np.tan(x)
y4 = np.sinc(x)

# Create the figure and axes
# We are creating a 4x1 layout initially
fig = plt.figure(figsize=(6, 12))

# First subplot for Sine function
ax1 = fig.add_subplot(4, 1, 1)
ax1.plot(x, y1, 'r-')
ax1.set_title("Sine Wave")
ax1.set_xlabel("Angle [rad]")
ax1.set_ylabel("Value")
ax1.grid(True)

# Second subplot for Cosine function
ax2 = fig.add_subplot(4, 1, 2)
ax2.plot(x, y2, 'g-')
ax2.set_title("Cosine Wave")
ax2.set_xlabel("Angle [rad]")
ax2.set_ylabel("Value")
ax2.grid(True)

# Third subplot for Tangent function
ax3 = fig.add_subplot(4, 1, 3)
ax3.plot(x, y3, 'b-')
ax3.set_title("Tangent Wave")
ax3.set_ylim(-5, 5) # Limit y-axis for better visualization
ax3.set_xlabel("Angle [rad]")
ax3.set_ylabel("Value")
ax3.grid(True)

# Fourth subplot for Sinc function
ax4 = fig.add_subplot(4, 1, 4)
ax4.plot(x, y4, 'k-')
ax4.set_title("Sinc Function")
ax4.set_xlabel("Angle [rad]")
ax4.set_ylabel("Value")
ax4.grid(True)

# Adjust layout to prevent overlap
plt.tight_layout()

# Display the plot
plt.show()

# End of the script.