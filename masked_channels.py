# Clean version without the flags

import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator

# Path to the ALL_MASK directory
base_path = '/home/nour/Nancay/Rfifind-Masks/ALL_MASK'

def load_channel_counts(base_path):
    """
    Load and count channel flags from all mask files under base_path.
    Returns: channel_counts dict and total number of valid files.
    """
    channel_counts = {}
    valid_file_count = 0

    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.startswith('mask_zap_chans') and file.endswith('.txt'):
                file_path = os.path.join(root, file)
                try:
                    data = np.loadtxt(file_path, dtype=int)
                    if data.size == 0:
                        continue
                    elif data.ndim == 0:
                        data = [int(data)]

                    valid_file_count += 1
                    for chan in data:
                        channel_counts[chan] = channel_counts.get(chan, 0) + 1

                except Exception as e:
                    print(f"Skipping file {file_path} due to error: {e}")
    
    return channel_counts, valid_file_count

def plot_filtered_histograms(channel_counts, valid_file_count, threshold_percent=60):
    """
    Filters channels based on the threshold percentage, then plots
    cumulative count and percentage histograms excluding them.
    """
    all_channels = sorted(channel_counts.keys())
    counts = np.array([channel_counts[chan] for chan in all_channels])
    percentages = (counts / valid_file_count) * 100

    # Find channels to exclude
    excluded_channels = [chan for chan, perc in zip(all_channels, percentages) if perc >= threshold_percent]

    # Filter out excluded channels
    filtered_channels = [chan for chan in all_channels if chan not in excluded_channels]
    filtered_counts = np.array([channel_counts[chan] for chan in filtered_channels])
    filtered_percentages = (filtered_counts / valid_file_count) * 100

    # Plot 1: Cumulative count histogram (filtered)
    fig1, ax1 = plt.subplots(figsize=(8,6))
    ax1.bar(filtered_channels, filtered_counts, color='darkblue', edgecolor='blue')
    ax1.set_xlabel('Channel ID')
    ax1.set_ylabel('Count')
    ax1.set_title(f'Cumulative Count (Channels < {threshold_percent}%)')
    ax1.grid(which='major', linestyle='-', linewidth=0.5, color='black')
    ax1.set_ylim(0, 100)
    ax1.xaxis.set_minor_locator(AutoMinorLocator(10))
    ax1.grid(which='minor', linestyle=':', linewidth=0.5, color='gray')

    # Plot 2: Cumulative percentage histogram (filtered)
    fig2, ax2 = plt.subplots(figsize=(14,8))
    ax2.bar(filtered_channels, filtered_percentages, color='red', edgecolor='red')
    ax2.set_xlabel('Channel ID')
    ax2.set_ylabel('Percentage (%)')
    ax2.set_title(f'Percentage of Files Each Channel Was Flagged In (< {threshold_percent}%)')
    ax2.set_ylim(0, 100)
    ax2.grid(which='major', linestyle='-', linewidth=0.5, color='black')
    ax2.xaxis.set_minor_locator(AutoMinorLocator(10))
    ax2.grid(which='minor', linestyle=':', linewidth=0.5, color='gray')

    plt.show()

    print(f'\nTotal valid mask files read: {valid_file_count}')
    print(f'Channels excluded (≥{threshold_percent}% of files):\n{excluded_channels}')
    return excluded_channels

# --- Usage example ---
channel_counts, valid_file_count = load_channel_counts(base_path)

# Set threshold percent you want to filter (e.g., 60%)
excluded = plot_filtered_histograms(channel_counts, valid_file_count, threshold_percent=60)
