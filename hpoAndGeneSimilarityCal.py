import pandas as pd
import csv
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


# 将所有disorder的gene关系表存为一个dic
def disorder_gene_dic(alldisorder):
    relationdic = dict()
    disorder_list = pd.read_csv('./origin_data/disease2gene.csv', header=None, index_col=0)
    disorder_list.columns = ['gene_symbol']
    for a in alldisorder:
        if type(disorder_list.loc[int(a), 'gene_symbol']) == str:
            term = [disorder_list.loc[int(a), 'gene_symbol']]
        else:
            term = list(disorder_list.loc[int(a), 'gene_symbol'].values)
        relationdic[a] = term
    return relationdic


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
def distinguish(list):
    hpo_group0 = []
    gene_group0 = []
    for a in list:
        if len(a) < 3:
            gene_group0.append(a)
        elif a[2] == ':' and len(a) == 10:
            hpo_group0.append(a)
        else:
            gene_group0.append(a)
    return hpo_group0, gene_group0


if __name__ == '__main__':
    all_hpo_disorder = find_hpo_disorder()
    all_orpha_hpo = find_orpha_hpo()
    disorder_s_hpo = disorder_hpo_dic(all_hpo_disorder)

    all_gene_disorder = find_gene_disorder()
    disorder_s_gene = disorder_gene_dic(all_gene_disorder)
    gene_dis = pd.read_csv('./origin_data/gene_distance.csv', header=0, index_col=0)

    data_group = list(set(translate(sys.argv[1:])))
    # data_group = ['HP:0000035', 'ATM', 'AGA', 'KIF7', 'CWC27', 'HP:0000147', 'HP:0045036']
    hpo_group, gene_group = distinguish(data_group)

    judge = 0
    for i in hpo_group:
        if i not in all_orpha_hpo:
            judge = 1
    if judge == 0:
        hpo_distance = pd.read_csv('./origin_data/hpo_distance.csv', header=0, index_col=0)
    else:
        hpo_distance = pd.DataFrame()
        for i in range(0, 15):
            part_distance = pd.read_csv('./origin_data/new_dis/new_hpo_distance_a' + str(i) + '.csv',
                                        index_col=0, header=0)
            hpo_distance = pd.concat([hpo_distance, part_distance], axis=1)

    hpo_disorder_dis = pd.Series(index=all_hpo_disorder)
    for j in range(len(all_hpo_disorder)):
        hpo_list = disorder_s_hpo[all_hpo_disorder[j]]
        if judge == 0:
            distance = mindistance(hpo_group, hpo_list, hpo_distance)/24
        else:
            distance = mindistance(hpo_group, hpo_list, hpo_distance)/25
        hpo_disorder_dis[all_hpo_disorder[j]] = distance
    hpo_result = hpo_disorder_dis.nsmallest(100)

    gene_disorder_dis = pd.Series(index=all_gene_disorder)
    for j in range(len(all_gene_disorder)):
        a_list = disorder_s_gene[all_gene_disorder[j]]
        b_list = translate(a_list)
        distance = mindistance(gene_group, b_list, gene_dis)
        gene_disorder_dis[all_gene_disorder[j]] = distance
    gene_result = gene_disorder_dis.nsmallest(100)

    complex_disorder = list(set(list(hpo_result.index.values) + list(gene_result.index.values)))
    complex_result = pd.Series()
    include_result = pd.Series()
    for i in complex_disorder:
        if i in list(hpo_result.index.values) and i in list(gene_result.index.values):
            complex_result[i] = (hpo_result[i] + gene_result[i])/2
            include_result[i] = 1
        elif i in list(hpo_result.index.values):
            complex_result[i] = hpo_result[i]
            include_result[i] = 3
        elif i in list(gene_result.index.values):
            complex_result[i] = gene_result[i]
            include_result[i] = 2
    complex_result = complex_result.nsmallest(100)
    final_frame = pd.DataFrame(columns=['dis', 'fre'], index=complex_result.index.values)
    for i in complex_result.index.values:
        final_frame['dis'][i] = complex_result[i]
        final_frame['fre'][i] = include_result[i]
    final_frame = final_frame.sort_values(by=['dis', 'fre'])
    for i in final_frame.index.values:
        print(i, final_frame['dis'][i], final_frame['fre'][i], sep=',', end=';')
