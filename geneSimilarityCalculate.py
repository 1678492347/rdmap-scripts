import pandas as pd
import csv
import sys


# 找出所有disorder
def find_disorder():
    with open('./origin_data/all_gene_disorder.csv', 'r') as all_disorder1:
        reader = csv.reader(all_disorder1)
        rows = [row for row in reader]
        bb = []
        for a in rows:
            bb.append(a[0])
    return bb


# 将所有disorder的hpo关系表存为一个dic
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


if __name__ == '__main__':
    all_disorder = find_disorder()
    disorder_s_gene = disorder_gene_dic(all_disorder)
    gene_dis = pd.read_csv('./origin_data/gene_distance.csv', header=0, index_col=0)

    gene_group = list(set(translate(sys.argv[1:])))
    disorder_dis = pd.Series(index=all_disorder)
    for j in range(len(all_disorder)):
        a_list = disorder_s_gene[all_disorder[j]]
        b_list = translate(a_list)
        distance = mindistance(gene_group, b_list, gene_dis)
        disorder_dis[all_disorder[j]] = distance
    result = disorder_dis.nsmallest(len(all_disorder))
    for i in result.index.values:
        print(i, result[i], sep=',', end=';')
