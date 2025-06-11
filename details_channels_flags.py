## overlaid plots of all files + cumulative


import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.cm as cm
import re
import time


###############-------- Utility Functions --------##############

## def for the plot namings pulsar name + date

## Remove "MASK_BS_" followed by digits and underscore using regex

def raj_dec(filename):
	rest = re.sub(r"^MASK_BS_\d+_(\d+\+\d+)_\d+_(\d+_\d+)$", r"\1_\2", filename)
	return rest


#############------------Collect data from directory---------------####################


# Define the main directory where all subdirectories exist
main_dir = "/home/nour/Nancay/Rfifind-Masks/ALL_MASK"  # Change this to any directory


#creating a list to save all the paths of each file in the subdir

mask_files = []


for subdir in sorted(os.listdir(main_dir)):  
    subdir_path = os.path.join(main_dir, subdir) #joining  main_dir path + subdir path example: /home/..../Rfifind_Masks/MASK_BS_1234
    
    if os.path.isdir(subdir_path):  # Check if it's a directory

        # Loop through all files in the subdirectory	
        for file in sorted(os.listdir(subdir_path)):
            file_path = os.path.join(subdir_path, file)
            if os.path.isfile(file_path):  # Ensure it's a file
                if os.path.getsize(file_path) == 0:
                  print(f"Empty file: {os.path.basename(file_path)}")
                else:
                  mask_files.append(file_path)  # Append the full path

                  
        #output: /home/nour/Nancay/Rfifind-Masks/MASK_BS_2312_122512+744239_20230319_000034_2/mask_zap_chans_3.txt = filepath
        #       -------------------------------subdir_path----------------------------------  --------file--------        
        #       -----------------------------------------file_path-------------------------------------------------

########################################################################################################

## now we prepare for all the plots

nbr_files = len(mask_files)

## Input paramerters:
nbrf = 24756;
nar = np.arange(nbrf) + 1


######------Creating the figures------########


start_flag = 0
end_flag = 24756
bin_range = end_flag - start_flag
channels = np.arange(start_flag,end_flag)

# Initialize the cumulative histogram
cumulative_counts = np.zeros(nbrf, dtype=int)

print("starting with the loop")
start_time = time.time()


# Loop through all mask files
for i, file_path in enumerate(mask_files):
    print(os.path.basename(file_path))

    # Load data
    try:
        data = pd.read_csv(file_path, delimiter=',', header=None)
        if data.isnull().values.any():
            print(f"NaN found in {file_path}")
            continue
        subdir = os.path.basename(os.path.dirname(file_path))
        title = raj_dec(subdir)
        fdata = data.values.flatten()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        continue

    # Second try block: Updating the cumulative histogram
    try:
        data = data.squeeze()
        if data.empty:
            continue
        valid_channels = data[(data >= start_flag) & (data < end_flag)].astype(int)
        for ch in valid_channels:
            if 0 <= ch < nbrf:
                cumulative_counts[ch] += 1
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")


end_time = time.time()
print('end of loop')
print('Elapsed time: ', end_time - start_time)


ch_list = []


for channel, count in enumerate(cumulative_counts):
    if count > 80:
        print(f"Channel {channel}: {count} flags")
        ch_list.append(channel)
print(f'Length of channel list is: {len(ch_list)}')
print(ch_list)


# Plot: cumulative histogram
plt.figure(figsize=(16, 10))
plt.bar(nar, cumulative_counts, width=1.0, color='red')
plt.xticks(np.arange(0, end_flag + 1, 1000))
plt.yticks(np.arange(0, 100 + 1, 10))
plt.xlabel("Channel ID")
plt.ylabel("Count of observation flagged")
plt.title("Cumulative Histogram: Channel Flag Counts")
plt.grid(True)
plt.tight_layout()
plt.show()
