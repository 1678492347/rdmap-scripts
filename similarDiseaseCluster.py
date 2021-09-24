import sys
import pandas as pd

check_id = sys.argv[1]

cluster_frame = pd.read_csv('origin_data/disorder_hpo_cluster17.csv', header=None, index_col=None)
cluster_series = pd.Series(data=cluster_frame[0].values, index=cluster_frame[1].values)
disease_index = cluster_series[cluster_series == int(check_id)].index.values

distance_frame = pd.read_csv('origin_data/disorder_distance.csv', header=0, index_col=0)
frame1 = distance_frame[check_id][cluster_series[disease_index[0]].values].sort_values()
frame2 = pd.DataFrame(columns=['orphan_number', 'distance'])
frame2['orphan_number'] = frame1.index.values
frame2['distance'] = frame1.values
for i in range(len(frame2)):
    print(frame2['orphan_number'][i], frame2['distance'][i], sep=',', end=';')
