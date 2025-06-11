import os                                                                                      
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# Path to the main directory
main_dir = "/home/nour/Nancay/Rfifind-Masks/ALL_MASK"

# Frequency range
start_flag = 0 #21200
end_flag = 24756
bin_range = end_flag - start_flag
channels = np.arange(start_flag,end_flag)

# Initialize count array
cumulative_counts = np.zeros(bin_range, dtype=int)

# Collect mask files
mask_files = []
for subdir in sorted(os.listdir(main_dir)):
    subdir_path = os.path.join(main_dir, subdir)
    if os.path.isdir(subdir_path):
        for file in os.listdir(subdir_path):
            file_path = os.path.join(subdir_path, file)
            if os.path.isfile(file_path) and os.path.getsize(file_path) > 0:
                mask_files.append(file_path)
            elif os.path.getsize(file_path) == 0:
                print(f"Empty file skipped: {os.path.basename(file_path)}")

# Process mask files
for file_path in mask_files:
    try:
        data = pd.read_csv(file_path, header=None).squeeze()
        if data.empty:
            continue
        valid_data = data[(data >= start_flag) & (data < end_flag)].astype(int)
        for val in valid_data:
            cumulative_counts[val - start_flag] += 1
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")

# Stats
total_files = len(mask_files)
max_count = np.max(cumulative_counts)    ##nbr of files 
max_bins = np.where(cumulative_counts == max_count)[0] + start_flag

print(f"Total mask files: {total_files}")
print(f"Max count: {max_count}")
#print(f"Bin(s) with highest count: {max_bins}, length: {len(max_bins)}")

# Threshold logic (90% example)
percent = 85
#threshold = int((percent / 100) * total_files)      #it is in %
threshold = 80

high_bins = np.where(cumulative_counts >= threshold)[0] + start_flag
high_counts = cumulative_counts[cumulative_counts >= threshold]

print(f"Bins flagged in ≥{percent}% of files (≥{threshold} times): {high_bins}, length: {len(high_bins)}")


# Bins with max count not in high bins (should be empty)
notsamebin = [x for x in max_bins if x not in high_bins]
print("Max bins NOT in high_bins:", notsamebin)


print('length of data', len(data))
print('length of the range', len(valid_data))
print('length of cumulative list', len(cumulative_counts))



thresholds = np.arange(0, 100)  # Thresholds from 0% to 100%
masked_channels = []

print(masked_channels)
print('mask', len(masked_channels))
print('length thresh', len(thresholds))


######   FIGURE 1:  HISTORGRAM COUNT OF FILES % PER CHANNEL ID ######
plt.figure(1,figsize=(16, 10))
plt.bar(channels, cumulative_counts, width=1.0, color='red')
plt.xticks(np.arange(0, end_flag + 1, 1000))
plt.yticks(np.arange(0, 100 + 1, 10))
plt.xlabel("Frequency Bin")
plt.ylabel("Cumulative count of Flags")
plt.title("Cumulative Mask Histogram (Flag Count vs. Frequency Bin)")
plt.grid(True)



###### FIG 2: HISTOGRAM TO CHECK THE MINIMUM THRESHOLD TO REMOVE TO MASK ######
#plt.figure(2, figsize =(16, 10))
#plt.bar(cumulative_counts, channels, color='blue')
#plt.xlabel(' % Threshold')
#plt.ylabel('% of Channel ID')
#plt.title('Effect of masking at threshold')
#plt.grid()


plt.tight_layout()
plt.show()






