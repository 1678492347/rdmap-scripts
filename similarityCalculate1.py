import pandas as pd
import csv
import sys


# 找出所有disorder
def find_disorder():
    with open('./origin_data/all_disorder.csv', 'r') as all_disorder1:
        reader = csv.reader(all_disorder1)
        rows = [row for row in reader]
        bb = []
        for a in rows:
            bb.append(a[0])
    return bb


# 找出所有有关orphaDisease的hpo
def find_orpha_hpo():
    with open('./origin_data/all_orpha_hpo.csv', 'r') as all_orpha_hpo1:
        reader = csv.reader(all_orpha_hpo1)
        rows = [row for row in reader]
        bb = []
        for a in rows:
            bb.append(a[0])
    return bb


# 将所有disorder的hpo关系表存为一个dic
def disorder_hpo_dic(alldisorder):
    relationdic = dict()
    disorder_list = pd.read_csv('./origin_data/disordertohpo(no0)sorted1.csv', header=None, index_col=0)
    disorder_list.columns = ['hpo', 'fre']
    for a in alldisorder:
        if type(disorder_list.loc[int(a), 'hpo']) == str:
            term = [disorder_list.loc[int(a), 'hpo']]
        else:
            term = list(disorder_list.loc[int(a), 'hpo'].values)
        relationdic[a] = term
    return relationdic


# 最小距离
def mindistance(list1, list2, dislis):
    total_dis = 0
    times = 0
    for a in list1:
        distance1 = 100
        for b in list2:
            result = dislis[a][b]
            if result < distance1:
                distance1 = result
        total_dis += distance1
        times += 1
    return total_dis/times


if __name__ == '__main__':
    all_disorder = find_disorder()
    all_orpha_hpo = find_orpha_hpo()
    disorder_s_hpo = disorder_hpo_dic(all_disorder)
    
    hpo_group = list(set(sys.argv[1:]))
    # hpo_group = ['HP:0000035', 'HP:0000147', 'HP:0045036']

    judge = 0
    for i in hpo_group:
        if i not in all_orpha_hpo:
            judge = 1
    if judge == 0:
        hpo_distance = pd.read_csv('./origin_data/hpo_distance.csv', header=0, index_col=0)
        hpo_distance = hpo_distance.apply(pd.to_numeric, downcast='unsigned')
    else:
        hpo_distance = pd.DataFrame()
        for i in range(0, 15):
            part_distance = pd.read_csv('./origin_data/new_dis/new_hpo_distance_a' + str(i) + '.csv',
                                        index_col=0, header=0)
            convert_part_distance = part_distance.apply(pd.to_numeric, downcast='unsigned')
            # hpo_distance = pd.concat([hpo_distance, part_distance], axis=1)
            hpo_distance = pd.concat([hpo_distance, convert_part_distance], axis=1)
    disorder_dis = pd.Series(index=all_disorder)
    for j in range(len(all_disorder)):
        hpo_list = disorder_s_hpo[all_disorder[j]]
        if judge == 0:
            distance = mindistance(hpo_group, hpo_list, hpo_distance)/24
        else:
            distance = mindistance(hpo_group, hpo_list, hpo_distance)/25
        disorder_dis[all_disorder[j]] = distance
    # result = disorder_dis.nsmallest(100)
    result = disorder_dis.nsmallest(len(all_disorder))
    for i in result.index.values:
        print(i, result[i], sep=',', end=';')
