import sys
import pandas as pd

check_id = sys.argv[1]

frame = pd.read_csv('origin_data/disorder_distance.csv', header=0, index_col=0)
frame1 = frame[check_id].sort_values()
frame2 = pd.DataFrame(columns=['orphan_number', 'distance'])
frame2['orphan_number'] = frame1.index.values
frame2['distance'] = frame1.values
for i in range(len(frame2)):
    print(frame2['orphan_number'][i], frame2['distance'][i], sep=',', end=';')
