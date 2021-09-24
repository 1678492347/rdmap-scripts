import pandas as pd
import csv
# from time import time
import sys


# # memory优化
# def mem_usage(pandas_obj):
#     if isinstance(pandas_obj, pd.DataFrame):
#

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
    with open('./origin_data/all_orpha_hpo.csv', 'r', encoding='UTF-8-sig') as all_orpha_hpo1:
        reader = csv.reader(all_orpha_hpo1)
        rows = [row for row in reader]
        bb = []
        for a in rows:
            bb.append(a[0])
    return bb


def find_hpo_index():
    global hpo_index
    # 说明：part_dis包括五千多种罕见病中的表型，new_dis是一万四千多个所有的表型异常
    with open('./origin_data/part_dis/index.csv', 'r') as file:
        reader = csv.reader(file)
        rows = [row for row in reader]
        for a in rows:
            hpo_index.append(a)
    with open('./origin_data/new_dis/hpo_index.csv', 'r') as file:
        reader = csv.reader(file)
        rows = [row for row in reader]
        for a in rows:
            hpo_index.append(a)


# 将所有disorder的hpo关系表存为一个dic
def disorder_hpo_dic():
    relationdic = dict()
    term = []
    with open('./origin_data/disordertohpo(no0)sorted1.csv', 'r') as csvfile:
        reader = csv.reader(csvfile)
        disorder_list = [row for row in reader]
    this_disorder = disorder_list[0][0]
    for a in disorder_list:
        if a[0] == this_disorder:
            term.append(a[1])
        else:
            relationdic[this_disorder] = term
            this_disorder = a[0]
            term = [a[1]]
    relationdic[this_disorder] = term
    return relationdic
    # disorder_list = pd.read_csv('./origin_data/disordertohpo(no0)sorted1.csv', header=None, index_col=0)
    # disorder_list.columns = ['hpo', 'fre']
    # for a in alldisorder:
    #     if type(disorder_list.loc[int(a), 'hpo']) == str:
    #         term = [disorder_list.loc[int(a), 'hpo']]
    #     else:
    #         term = list(disorder_list.loc[int(a), 'hpo'].values)
    #     relationdic[a] = term
    # return relationdic


# 最小距离
def mindistance(list1, list2, dislis1, dislis2):
    global all_orpha_hpo
    total_dis = 0
    times = 0
    for a in list1:
        if a in all_orpha_hpo:
            dislis = dislis1
            div = 24
        else:
            dislis = dislis2
            div = 25
        distance1 = 100
        for b in list2:
            result = dislis[a][b]/div
            if result < distance1:
                distance1 = result
        total_dis += distance1
        times += 1
    return total_dis / times


if __name__ == '__main__':
    all_disorder = find_disorder()
    all_orpha_hpo = find_orpha_hpo()
    disorder_s_hpo = disorder_hpo_dic()
    # print('Time used: {} sec'.format(time() - tt))

    hpo_group = list(set(sys.argv[1:]))
    # hpo_group = ['HP:0000256', 'HP:0000035', 'HP:0003537']
    # hpo_group = ['HP:0003537']

    # tt = time()
    hpo_index = []
    find_hpo_index()
    file_index = []
    for hpo in hpo_group:
        for i in range(len(hpo_index)):
            if hpo in hpo_index[i]:
                file_index.append(i)
                break
    file_index = list(set(file_index))

    hpo_distance1 = pd.DataFrame()
    hpo_distance2 = pd.DataFrame()
    for i in file_index:
        if i < 11:
            part_distance = pd.read_csv('./origin_data/part_dis/part_distance_' + str(i) + '.csv', index_col=0, header=0)
            hpo_distance1 = pd.concat([hpo_distance1, part_distance], axis=1)
        else:
            part_distance = pd.read_csv('./origin_data/new_dis/new_hpo_distance_a' + str(i-11) + '.csv', index_col=0,
                                        header=0)
            convert_part_distance = part_distance.apply(pd.to_numeric, downcast='unsigned')
            hpo_distance2 = pd.concat([hpo_distance2, convert_part_distance], axis=1)
    # print('Time used: {} sec'.format(time() - tt))

    # tt = time()
    disorder_dis = pd.Series(index=all_disorder, dtype=float)
    for i in range(len(all_disorder)):
        hpo_list = disorder_s_hpo[all_disorder[i]]
        distance = mindistance(hpo_group, hpo_list, hpo_distance1, hpo_distance2)
        disorder_dis[all_disorder[i]] = distance
    # print(disorder_dis)
    result = disorder_dis.nsmallest(len(all_disorder))
    for i in result.index.values:
        print(i, round(result[i], 4), sep=',', end=';')








    # tt = time()
    # judge = 0
    # for i in hpo_group:
    #     if i not in all_orpha_hpo:
    #         judge = 1
    # if judge == 0:
    #     # hpo_distance = pd.read_csv('./origin_data/hpo_distance.csv', header=0, index_col=0)
    #     hpo_distance = pd.read_csv('./origin_data/hpo_distance.gz', header=0, index_col=0)
    #     hpo_distance = hpo_distance.apply(pd.to_numeric, downcast='unsigned')
    # else:
    #     hpo_distance = pd.DataFrame()
    #     for i in range(0, 15):
    #         part_distance = pd.read_csv('./origin_data/new_dis/new_hpo_distance_a' + str(i) + '.csv',
    #                                     index_col=0, header=0)
    #         convert_part_distance = part_distance.apply(pd.to_numeric, downcast='unsigned')
    #         # hpo_distance = pd.concat([hpo_distance, part_distance], axis=1)
    #         hpo_distance = pd.concat([hpo_distance, convert_part_distance], axis=1)
    # print('Time used: {} sec'.format(time() - tt))
    # print(hpo_distance)
    # print(hpo_distance.dtypes)
    # print(hpo_distance.info(memory_usage='deep'))
    # hpo_distance.to_csv('./origin_data/hpo_distance.gz', compression='gzip')
    # print('--------------------------------------')
    # hpo_distance_int = hpo_distance.select_dtypes(include=['int'])
    # convert_hpo_distance = hpo_distance_int.apply(pd.to_numeric, downcast='unsigned')
    # print(convert_hpo_distance)
    # print(convert_hpo_distance.dtypes)
    # print(convert_hpo_distance.info(memory_usage='deep'))
    # hpo_distance = convert_hpo_distance

    # disorder_dis = pd.Series(index=all_disorder, dtype=float)
    # for j in range(len(all_disorder)):
    #     hpo_list = disorder_s_hpo[all_disorder[j]]
    #     if judge == 0:
    #         distance = mindistance(hpo_group, hpo_list, hpo_distance) / 24
    #     else:
    #         distance = mindistance(hpo_group, hpo_list, hpo_distance) / 25
    #     disorder_dis[all_disorder[j]] = distance
    # result = disorder_dis.nsmallest(100)
    # for i in result.index.values:
    #     print(i, result[i], sep=',', end=';')
