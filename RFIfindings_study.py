import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.cm as cm
import re

# =================== Utility Functions ===================

def time_classification(filename):
    match = re.search(r'(\d{6}_\d+)$', filename)
    return match.group(1) if match else None

def raj_dec(filename):
    return re.sub(r"^MASK_BS_\d+_(\d+\+\d+)_\d+_(\d+_\d+)$", r"\1_\2", filename)

def sort_time(subdir):
    match = re.match(r"^MASK_BS_\d+_\d+\+\d+_\d+_(\d+_\d+)$", subdir)
    if match:
        t1, t2 = map(int, match.group(1).split('_'))
        return (t1, t2)
    return (float('inf'), float('inf'))

def extract_time(file_path):
    subdir = os.path.basename(os.path.dirname(file_path))
    return sort_time(subdir)

# =================== Plotting Functions ===================

def time_dependent_sub(ax, data, title, subdir, i, cols, rows):
    ax.hist(data.values.flatten(), bins=200, color='red', label=f"{subdir}")
    ax.set_yscale('log')
    ax.set_ylim(1, 260)
    ax.set_xlim(20000, 24756)
    ax.set_title(f"{title}", fontsize=6)
    ax.grid(True)
    ax.set_xticks(ax.get_xticks())
    ax.set_yticks(ax.get_yticks())
    ax.tick_params(axis='both', labelsize=2.7)
    if i % cols == 0:
        ax.set_ylabel("Count")
    if i // cols == rows - 1:
        ax.set_xlabel("Channels")

def overlaid_histograms(ax, mask_files, colors):
    for i, file_path in enumerate(mask_files):
        data = pd.read_csv(file_path, delimiter=',')
        subdir = os.path.basename(os.path.dirname(file_path))
        title = raj_dec(subdir)
        fdata = data.values.flatten()
        ax.hist(fdata, bins=range(22000, 23000), alpha=0.5, color=colors(i), label=f"{title}")
    ax.set_xlabel("Channels")
    ax.set_ylabel("Count")
    ax.set_title("Histogram for MASK_BS_ALL")
    ax.grid(True)

def plot_4beam_grouped_histograms(main_dir):
    grouped_files = {0: [], 1: [], 2: [], 3: []}

    for subdir in sorted(os.listdir(main_dir)):
        subdir_path = os.path.join(main_dir, subdir)
        if os.path.isdir(subdir_path):
            match = re.search(r'_(\d)$', subdir)
            if match:
                group_id = int(match.group(1))
                if group_id in grouped_files:
                    for file in os.listdir(subdir_path):
                        file_path = os.path.join(subdir_path, file)
                        if os.path.isfile(file_path) and os.path.getsize(file_path) > 0:
                            grouped_files[group_id].append(file_path)

    cols = 4
    rows = max(len(grouped_files[i]) for i in range(4))
    if rows == 0:
        print("No data to plot.")
        return

    fig, axes = plt.subplots(rows, cols, figsize=(cols * 4, rows * 9))
    axes = np.atleast_2d(axes)
    if rows == 1:
        axes = axes[np.newaxis, :]

    total_files = sum(len(grouped_files[i]) for i in range(4))
    colors = cm.get_cmap('nipy_spectral', total_files)
    color_index = 0

    for col_index in range(cols):
        files = grouped_files[col_index]
        for row_index, file_path in enumerate(files):
            data = pd.read_csv(file_path, delimiter=',')
            subdir = os.path.basename(os.path.dirname(file_path))
            title = raj_dec(subdir)
            ax = axes[row_index, col_index]
            ax.hist(data.values.flatten(), bins=250, color=colors(color_index))
            ax.set_yscale('log')
            ax.set_ylim(1, 260)
            ax.set_xlim(0, 24756)
            ax.set_title(title, fontsize=5.0)
            ax.grid(True)
            ax.tick_params(axis='both', labelsize=4)

            if row_index == rows - 1:
                ax.set_xlabel("Channels", fontsize=5.0)
            if col_index == 0:
                ax.set_ylabel("Count", fontsize=5.0)

            color_index += 1

    for col_index in range(cols):
        for row_index in range(len(grouped_files[col_index]), rows):
            fig.delaxes(axes[row_index, col_index])

    plt.tight_layout(pad=5.0)
    plt.show()

# =================== Main Execution ===================

main_dir = "/home/nour/Nancay/Rfifind-Masks/ALL_MASK"
mask_files = []

for subdir in sorted(os.listdir(main_dir)):
    subdir_path = os.path.join(main_dir, subdir)
    if os.path.isdir(subdir_path):
        for file in os.listdir(subdir_path):
            file_path = os.path.join(subdir_path, file)
            if os.path.isfile(file_path) and os.path.getsize(file_path) > 0:
                mask_files.append(file_path)

mask_files = sorted(mask_files, key=extract_time)

# Plot 1: Overlaid Histogram
colors = cm.get_cmap('nipy_spectral', len(mask_files))
fig1, ax1 = plt.subplots(figsize=(16, 10))
overlaid_histograms(ax1, mask_files, colors)
plt.tight_layout()
plt.show()

# Plot 2: Time-dependent Subplots
nbr_files = len(mask_files)
cols = 8
rows = (nbr_files // cols) + (nbr_files % cols > 0)
fig2, axes = plt.subplots(rows, cols, figsize=(30, 2 * rows))
axes = axes.flatten()

for i, file_path in enumerate(mask_files):
    data = pd.read_csv(file_path, delimiter=',')
    subdir = os.path.basename(os.path.dirname(file_path))
    title = raj_dec(subdir)
    time_dependent_sub(axes[i], data, title, subdir, i, cols, rows)

for j in range(nbr_files, rows * cols):
    fig2.delaxes(axes[j])

plt.tight_layout(pad=4.0)
plt.show()

# Plot 3: 4-beam Grouped Histograms
plot_4beam_grouped_histograms(main_dir)

