# cumulative distribution of the bad channels from NenuFAR observations, in numbers and percentage
# makes 2 plots, and gives a list of the channels above the desired % (useful for rfifind in PRESTO)


import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator

# Path to the ALL_MASK directory
base_path = '/home/nour/Nancay/Rfifind-Masks/ALL_MASK'  # change directory path to your own path

## Observation data usually is in teh following format
## Big directory ( ALL_MASK ) > Subdirectories ( example: MASK_BS_2083_174137+693355_20220504_023035_0) > file.txt (mask_zap_chans_0.txt) ##

# Dictionary to count occurrences of each flagged channel
channel_counts = {}

# Counter for number of successfully read mask files
valid_file_count = 0

# Loop through subdirectories and collect data
for root, dirs, files in os.walk(base_path):
    for file in files:
        if file.startswith('mask_zap_chans') and file.endswith('.txt'):
            file_path = os.path.join(root, file)
            try:
                data = np.loadtxt(file_path, dtype=int)
                # Handle scalar values
                if data.size == 0:
                    continue
                elif data.ndim == 0:
                    data = [int(data)]

                valid_file_count += 1

                for chan in data:
                    channel_counts[chan] = channel_counts.get(chan, 0) + 1

            except Exception as e:
                print(f"Skipping file {file_path} due to error: {e}")

# Prepare cumulative data
all_channels = sorted(channel_counts.keys())
counts = np.array([channel_counts[chan] for chan in all_channels])
percentages = (counts / valid_file_count) * 100
# Threshold reporting
thresh_60 = [chan for chan, perc in zip(all_channels, percentages) if perc >= 60]
thresh_70 = [chan for chan, perc in zip(all_channels, percentages) if perc >= 70]

# Plot 1: Cumulative count histogram
fig1, ax1 = plt.subplots()
ax1.bar(all_channels, counts, color='steelblue', edgecolor='black')
ax1.set_xlabel('Channel ID')
ax1.set_ylabel('Count')
ax1.set_title('Cumulative Count of Flagged Channels')
ax1.grid(which='major', linestyle='-', linewidth=0.5, color='black')
ax1.xaxis.set_minor_locator(AutoMinorLocator(5))
ax1.grid(which='minor', linestyle=':', linewidth=0.5, color='gray')

# Plot 2: Cumulative percentage histogram
fig2, ax2 = plt.subplots()
ax2.bar(all_channels, percentages, color='mediumseagreen', edgecolor='black')
ax2.set_xlabel('Channel ID')
ax2.set_ylabel('Percentage (%)')
ax2.set_title('Percentage of Files Each Channel Was Flagged In')
ax2.grid(which='major', linestyle='-', linewidth=0.5, color='black')
ax2.xaxis.set_minor_locator(AutoMinorLocator(5))
ax2.grid(which='minor', linestyle=':', linewidth=0.5, color='gray')


print(f'\nTotal valid mask files read: {valid_file_count}')
print(f'Channels flagged in ≥60% of files ({len(thresh_60)} channels):\n{thresh_60}')
print(f'Channels flagged in ≥70% of files ({len(thresh_70)} channels):\n{thresh_70}')

plt.show()
