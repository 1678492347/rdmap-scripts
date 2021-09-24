import pandas as pd
import csv
from scipy.optimize import linear_sum_assignment
import numpy as np
import sys


# 找出所有有关hpo的disorder
def find_hpo_disorder():
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


# 找出所有有关gene的disorder
def find_gene_disorder():
    with open('./origin_data/all_gene_disorder.csv', 'r') as all_disorder1:
        reader = csv.reader(all_disorder1)
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


# 根据表型match相关疾病
def disorder_hpo(hpo1):
    disorder_list = pd.read_csv('./origin_data/disordertohpo(no0)sorted1.csv', header=None, index_col=1)
    disorder_list.columns = ['disorder', 'fre']
    if type(disorder_list.loc[hpo1, 'disorder']) == int:
        term = [str(disorder_list.loc[hpo1, 'disorder'])]
    else:
        term = [str(x) for x in list(disorder_list.loc[hpo1, 'disorder'].values)]
    return term


# 根据基因match相关疾病
def disorder_gene(gene1):
    disorder_list = pd.read_csv('./origin_data/disease2gene.csv', header=None, index_col=1)
    disorder_list.columns = ['disorder']
    if type(disorder_list.loc[gene1, 'disorder']) == np.int64:
        term = [str(disorder_list.loc[gene1, 'disorder'])]
    else:
        term = [str(x) for x in list(disorder_list.loc[gene1, 'disorder'].values)]
    return term


def mindistance(list1, list2, dislis):
    total_dis = 0
    times1 = 0
    for a in list1:
        distance1 = 100
        for b in list2:
            result1 = dislis[a][b]
            if result1 < distance1:
                distance1 = result1
        total_dis += distance1
        times1 += 1
    return total_dis/times1


# 弥补csv表格index的bug
def translate(list0):
    list1 = []
    for a in list0:
        if a == 'SEPT9':
            list1.append('9-Sep')
        elif a == 'SEPT12':
            list1.append('12-Sep')
        elif a == 'SEPT14':
            list1.append('14-Sep')
        else:
            list1.append(a)
    return list1


# 识别基因或表型
def distinguish(list1):
    hpo_group0 = []
    gene_group0 = []
    for a in list1:
        if len(a) < 3:
            gene_group0.append(a)
        elif a[2] == ':' and len(a) == 10:
            hpo_group0.append(a)
        else:
            gene_group0.append(a)
    return hpo_group0, gene_group0


def find_match(list1):
    num = 0
    for a in list1:
        if a == 0:
            num += 1
    return num


# 根据表型进行异常基因致病性rank的计算思路
# 一、对单个表型逐个分析与基因对关系
#     一个表型match一组疾病A，一个基因match一组疾病Bi（i=0,1,2,3...）
#     将两个疾病集A,Bi映射到疾病距离矩阵（hpo or gene？），得到一个子矩阵
#     km算法得到该矩阵的最小加权匹配结果Ri（i=0,1,2,3...）
#     根据该结果，对异常基因进行rank，rank信息包括最小加权匹配结果（主），两个疾病集A,Bi的大小（次）
# 二、分析基因和一组表型的关系
#     对一组表型进行相似疾病推荐，得到一个所有疾病的rank
#     1、每个基因match一组疾病，这一组疾病在疾病rank中的排名作为该基因对一组表型的关联程度
#     2、每个基因都和所有rank中的疾病进行相似性计算（计算量巨大并且不容易计算最终的关联程度，先不用）
# 如果输入的仅有一个表型，用（一）中的方法
if __name__ == '__main__':
    all_hpo_disorder = find_hpo_disorder()
    all_gene_disorder = find_gene_disorder()
    all_orpha_hpo = find_orpha_hpo()
    all_hpo_gene_disorder = list(set(all_hpo_disorder).intersection(set(all_gene_disorder)))  # 使用intersection求a与b的交集

    data_group = list(set(translate(sys.argv[1:])))
    # data_group = ['HP:0000035', 'ATM', 'AGA', 'KIF7', 'CWC27', 'HP:0000147', 'HP:0045036']
    hpo_group, gene_group = distinguish(data_group)

    disorder_gene_distance = pd.read_csv('./origin_data/disorder_gene_distance.csv', header=0, index_col=0)

    # 对单个表型逐个分析与基因对关系
    result = ''

    # 判断hpo_distance disorder_s_hpo有没有被加载
    load_hpo_distance = 0
    hpo_distance = pd.DataFrame()
    disorder_s_hpo = dict()

    for i in hpo_group:
        # 判断输入的hpo在不在罕见病表型里
        judge = 0
        # 如果输入的hpo不在罕见病表型里，那么就无法match罕见病，只能通过计算相似度，取出一些相似度高的疾病
        if i not in all_orpha_hpo:
            judge = 1
            if load_hpo_distance == 0:
                disorder_s_hpo = disorder_hpo_dic(all_hpo_gene_disorder)
                for j in range(0, 15):
                    part_distance = pd.read_csv('./origin_data/new_dis/new_hpo_distance_a' + str(j) + '.csv',
                                                index_col=0, header=0)
                    hpo_distance = pd.concat([hpo_distance, part_distance], axis=1)
                load_hpo_distance = 1

            hpo_group1 = [i]
            hpo_disorder_dis = pd.Series(index=all_hpo_gene_disorder)
            for j in range(len(all_hpo_gene_disorder)):
                hpo_list = disorder_s_hpo[all_hpo_gene_disorder[j]]
                distance = mindistance(hpo_group1, hpo_list, hpo_distance) / 25
                hpo_disorder_dis[all_hpo_gene_disorder[j]] = distance
            # 取出最相近的10个疾病
            disorder_hpo_1 = list(hpo_disorder_dis.nsmallest(10).index.values)
            disorder_hpo_1 = [str(x) for x in disorder_hpo_1]
        # 如果输入的hpo在罕见病表型里，那么就直接match罕见病
        else:
            disorder_hpo_1 = [x for x in disorder_hpo(i) if x in all_hpo_gene_disorder]

        result += i
        result_frame = pd.DataFrame(index=gene_group,
                                    columns=['distance', 'match', 'dis_gene_num', 'dis_hpo_num', 'matched_dis'])
        for j in gene_group:
            disorder_gene_1 = [int(x) for x in disorder_gene(j) if x in all_hpo_gene_disorder]
            distance_frame = disorder_gene_distance.loc[disorder_gene_1, disorder_hpo_1]
            distance_matrix = np.array(distance_frame)
            row_ind, col_ind = linear_sum_assignment(distance_matrix)
            distance_list = distance_matrix[row_ind, col_ind]
            matched_dis = ''
            if len(distance_list) > 0:
                distance = distance_list.sum() / len(distance_list)
                for k in range(len(distance_list)):
                    if distance_list[k] == 0:
                        matched_dis += str(disorder_gene_1[k])
                        matched_dis += ','
            else:
                distance = 'NaN'

            if matched_dis == '':
                matched_dis = 'NaN'
            else:
                matched_dis = matched_dis[:-1]

            result_frame['distance'][j] = distance
            if judge == 1:
                result_frame['match'][j] = 0
            else:
                result_frame['match'][j] = find_match(distance_list)
            result_frame['dis_hpo_num'][j] = len(disorder_hpo_1)
            result_frame['dis_gene_num'][j] = len(disorder_gene_1)
            result_frame['matched_dis'][j] = matched_dis
        result_frame.sort_values(axis=0, by=['distance', 'match', 'dis_hpo_num', 'dis_gene_num'],
                                 ascending=[True, False, True, True], inplace=True)
        for j in range(len(gene_group)):
            result += ';'
            result += result_frame.index.values[j]
            result += ','
            result += ','.join([str(x) for x in result_frame.iloc[j]])
        result += '&'
    result = result[:-1]

    # 分析基因和一组表型的关系
    if len(hpo_group) > 1:
        if load_hpo_distance == 0:
            disorder_s_hpo = disorder_hpo_dic(all_hpo_gene_disorder)
            hpo_distance = pd.read_csv('./origin_data/hpo_distance.csv', header=0, index_col=0)

        hpo_disorder_dis = pd.Series(index=all_hpo_gene_disorder)
        for i in range(len(all_hpo_gene_disorder)):
            hpo_list = disorder_s_hpo[all_hpo_gene_disorder[i]]
            if load_hpo_distance == 0:
                distance = mindistance(hpo_group, hpo_list, hpo_distance) / 24
            else:
                distance = mindistance(hpo_group, hpo_list, hpo_distance) / 25
            hpo_disorder_dis[all_hpo_gene_disorder[i]] = distance
        hpo_disorder_dis.sort_values(ascending=True, inplace=True)

        gene_rank = pd.Series(index=gene_group)
        for i in gene_group:
            disorder_gene_1 = [x for x in disorder_gene(i) if x in all_hpo_gene_disorder]
            if len(disorder_gene_1) > 0:
                dis = 0
                times = 0
                for j in disorder_gene_1:
                    dis += hpo_disorder_dis[j]
                    times += 1
                gene_rank[i] = dis/times
            else:
                gene_rank[i] = 'NaN'
        gene_rank.sort_values(ascending=True, inplace=True)
        result += '|'
        for i in range(len(gene_group)):
            result += gene_rank.index.values[i]
            result += ','
            result += str(gene_rank[i])
            result += ';'
        result = result[:-1]

    print(result)
