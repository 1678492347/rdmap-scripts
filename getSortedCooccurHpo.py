import pandas as pd
import numpy as np
from time import time
import csv
import sys


def find_hpo_index():
    global hpo_index
    with open('./origin_data/hpo_relation/hpo_relation_score_index.csv', 'r') as file:
        reader = csv.reader(file)
        rows = [row for row in reader]
        for a in rows:
            hpo_index.append(a)


if __name__ == '__main__':
    # t0 = time()
    top_n = int(sys.argv[2])
    this_hpo = [sys.argv[1]]
    # this_hpo = ['HP:0001252']
    hpo_index = []
    find_hpo_index()

    file_index = []
    for hpo in this_hpo:
        for i in range(len(hpo_index)):
            if hpo in hpo_index[i]:
                file_index.append(i)
                break
    file_index = list(set(file_index))

    hpo_relation_score = pd.DataFrame()
    for i in file_index:
        part_hpo_relation_score = pd.read_csv('./origin_data/hpo_relation/hpo_relation_score_' + str(i) + '.csv', index_col=0, header=0)
        convert_part_distance = part_hpo_relation_score.apply(pd.to_numeric, downcast='unsigned')
        hpo_relation_score = pd.concat([hpo_relation_score, part_hpo_relation_score], axis=1)
    # print(hpo_relation_score)
    this_hpo_score = hpo_relation_score[this_hpo[0]].nlargest(top_n)
    # this_hpo_score = this_hpo_score.sort_values(ascending=False)
    this_hpo_score = this_hpo_score[this_hpo_score > 0]
    # print(this_hpo_score)
    for i in this_hpo_score.index.values:
        print(i, this_hpo_score[i], sep=',', end=';')

