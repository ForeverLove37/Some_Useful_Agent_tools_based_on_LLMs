# Tool: Python
# Purpose: REFACTORED diagnostic visualization tool for survey plans.
# This script is designed to be a robust tool to analyze and verify the 
# output of the survey planning algorithm (o3.py). It can visualize the 
# coverage, calculate the final coverage boundary, and clearly show potential 
# gaps (leaks) or excessive overlaps, making it ideal for diagnosing issues
# like the one found in the original algorithm.

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from typing import List, Dict

# ----------------------------------------------------------------------
# 1: Mathematical Specification - Constants and Definitions
# (Copied from o3.py to make this script self-contained)
# ----------------------------------------------------------------------
X_MIN_NM = -2.0
X_MAX_NM = 2.0
Y_MIN_NM = -1.0
Y_MAX_NM = 1.0

D0_METERS = 110.0
ALPHA_DEG = 1.5
THETA_DEG = 120.0
NM_TO_M = 1852.0

# Pre-calculated values
alpha_rad = np.radians(ALPHA_DEG)
theta_rad = np.radians(THETA_DEG)
tan_alpha = np.tan(alpha_rad)
tan_half_theta = np.tan(theta_rad / 2)

# Discretization grid for accurate width calculation
# This MUST match the grid used in the main algorithm
DELTA_X_NM = 0.005
X_GRID = np.arange(X_MIN_NM, X_MAX_NM + DELTA_X_NM, DELTA_X_NM)

# ----------------------------------------------------------------------
# 2: Re-used Swath Width Function
# (Copied from o3.py for self-contained analysis)
# ----------------------------------------------------------------------
def get_swath_width(x_coordinate_nm: float) -> float:
    """
    Calculates the sonar swath width in nautical miles at a given
    East-West coordinate.
    """
    x_meters = x_coordinate_nm * NM_TO_M
    depth_meters = D0_METERS - x_meters * tan_alpha
    width_meters = 2 * depth_meters * tan_half_theta
    width_nm = width_meters / NM_TO_M
    return width_nm

# Pre-calculate all swath widths on the grid for efficiency
W_GRID = np.array([get_swath_width(x) for x in X_GRID])

# ----------------------------------------------------------------------
# 3: Refactored Visualization and Analysis Core
# ----------------------------------------------------------------------
def plot_survey_plan(ax: plt.Axes, survey_lines: pd.DataFrame):
    """
    Plots the individual survey swaths and their centerlines onto the axes.
    """
    print("Plotting survey swaths...")
    for _, line in survey_lines.iterrows():
        y = line['y_coordinate_nm']
        x_start = line['x_start_nm']
        x_end = line['x_end_nm']

        # Find the grid indices corresponding to the segment
        j_start = np.searchsorted(X_GRID, x_start)
        j_end = np.searchsorted(X_GRID, x_end)
        
        # Get the x and width values for this specific segment
        x_segment = X_GRID[j_start:j_end+1]
        w_segment = W_GRID[j_start:j_end+1]

        # Define the vertices of the coverage swath (a polygon)
        # It's a trapezoid because width varies with x
        swath_bottom = y - w_segment / 2
        swath_top = y + w_segment / 2
        
        vertices = list(zip(x_segment, swath_bottom)) + list(zip(x_segment[::-1], swath_top[::-1]))
        
        # Plot the semi-transparent swath polygon
        swath_patch = patches.Polygon(vertices, closed=True, facecolor='c', alpha=0.3, edgecolor='none')
        ax.add_patch(swath_patch)
        
        # Plot the survey centerline
        ax.plot([x_start, x_end], [y, y], color='blue', lw=1.0)

def calculate_and_plot_coverage_boundary(ax: plt.Axes, survey_lines: pd.DataFrame):
    """
    Calculates and plots the final northern coverage boundary.
    This is the most critical diagnostic plot, as it will reveal any gaps.
    """
    print("Calculating and plotting final coverage boundary...")
    # Start with the southern boundary of the survey area
    B_boundary = np.full_like(X_GRID, Y_MIN_NM)

    # Sequentially apply each survey line's coverage to the boundary
    for _, line in survey_lines.iterrows():
        y = line['y_coordinate_nm']
        x_start = line['x_start_nm']
        x_end = line['x_end_nm']

        j_start = np.searchsorted(X_GRID, x_start)
        j_end = np.searchsorted(X_GRID, x_end)

        # The new boundary is the top of the swath for this segment
        new_boundary_segment = y + W_GRID[j_start:j_end+1] / 2
        
        # Update the overall boundary, taking the maximum y-value at each point
        # This correctly handles overlapping swaths from different lines
        B_boundary[j_start:j_end+1] = np.maximum(B_boundary[j_start:j_end+1], new_boundary_segment)

    # Plot the final boundary
    ax.plot(X_GRID, B_boundary, color='red', lw=1.5, label='Final Coverage Boundary', zorder=10)
    
    # Check for gaps (leaks)
    min_final_coverage = np.min(B_boundary)
    if min_final_coverage < Y_MAX_NM:
        print(f"\nWARNING: Gaps detected! Minimum coverage reached only {min_final_coverage:.4f} nmi (target is {Y_MAX_NM:.4f} nmi).")
    else:
        print(f"\nSuccess! Full coverage achieved. Minimum final coverage is {min_final_coverage:.4f} nmi.")


def visualize_survey_plan(csv_filepath: str, title: str):
    """
    Main function to load a survey plan from a CSV and generate a
    diagnostic visualization.
    """
    try:
        survey_df = pd.read_csv(csv_filepath)
    except FileNotFoundError:
        print(f"Error: The file '{csv_filepath}' was not found.")
        print("Please run the main algorithm script (o3.py) first to generate the plan.")
        return

    fig, ax = plt.subplots(figsize=(16, 8))

    # 1. Plot the survey area boundary
    boundary_rect = patches.Rectangle((X_MIN_NM, Y_MIN_NM), X_MAX_NM - X_MIN_NM, Y_MAX_NM - Y_MIN_NM,
                                      linewidth=2, edgecolor='k', facecolor='none', label='Survey Area', zorder=5)
    ax.add_patch(boundary_rect)

    # 2. Plot the survey swaths and centerlines
    plot_survey_plan(ax, survey_df)
    
    # 3. Calculate and plot the crucial final coverage boundary
    calculate_and_plot_coverage_boundary(ax, survey_df)

    # 4. Final plot styling
    ax.set_aspect('equal', adjustable='box')
    ax.set_xlim(X_MIN_NM - 0.1, X_MAX_NM + 0.1)
    ax.set_ylim(Y_MIN_NM - 0.1, Y_MAX_NM + 0.1)
    ax.set_xlabel("East-West Coordinate (nautical miles)")
    ax.set_ylabel("North-South Coordinate (nautical miles)")
    ax.set_title(title, fontsize=16)
    ax.grid(True, linestyle='--', alpha=0.6)
    
    # Manually create a proxy artist for the swath patch for the legend
    swath_proxy = patches.Patch(color='c', alpha=0.3, label='Sonar Swath Coverage')
    centerline_proxy = plt.Line2D([0], [0], color='blue', lw=1, label='Survey Centerline')
    
    handles, labels = ax.get_legend_handles_labels()
    handles.extend([swath_proxy, centerline_proxy])
    ax.legend(handles=handles, loc='upper right')

    plt.show()

# ----------------------------------------------------------------------
# 4: Main Execution Block
# ----------------------------------------------------------------------
if __name__ == '__main__':
    # --- DIAGNOSTIC 1: Visualize the output from the ORIGINAL FLAWED code ---
    # This will clearly show the gaps (leaks) in coverage.
    print("="*70)
    print("Running Diagnostic 1: Visualizing output from ORIGINAL FLAWED code")
    print("="*70)
    original_csv_file = "problem3_east_west_survey_plan_REVISED.csv"
    visualize_survey_plan(
        csv_filepath=original_csv_file,
        title="Diagnostic Plot for ORIGINAL Flawed Algorithm"
    )

    # --- DIAGNOSTIC 2: Visualize the output from a CORRECTED code ---
    # After you fix o3.py (changing 0.8/0.9 to 0.3/0.4) and re-run it,
    # you would save the new CSV and visualize it here.
    # The red 'Final Coverage Boundary' line should be entirely above Y_MAX_NM.
    print("\n" + "="*70)
    print("Running Diagnostic 2: Visualizing output from a CORRECTED code")
    print("="*70)
    # Assumes you have saved the corrected output to a new file.
    # If not, this part will raise a FileNotFoundError.
    corrected_csv_file = "problem3_survey_plan_PARTITIONED.csv" 
    visualize_survey_plan(
        csv_filepath=corrected_csv_file,
        title="Verification Plot for CORRECTED Algorithm"
    )