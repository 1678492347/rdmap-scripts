import pandas as pd
import numpy as np
from sklearn import manifold
import sys

if __name__ == '__main__':
    hpo_group = list(set(sys.argv[1:]))
    # hpo_group = ['HP:0000132', 'HP:0000010', 'HP:0000256', 'HP:0000272', 'HP:0000316', 'HP:0000369', 'HP:0000470', 'HP:0000767', 'HP:0001274', 'HP:0001373', 'HP:0001513', 'HP:0002007', 'HP:0001250', 'HP:0001249', 'HP:0000118']

    class_frame = pd.read_csv('./origin_data/hpo_class.csv', header=0, index_col=0, encoding='utf8')
    sub_class_frame = class_frame.loc[hpo_group, ['class']]
    all_class = []
    for i in sub_class_frame.index.values:
        if pd.isnull(sub_class_frame.loc[i, 'class']):
            sub_class_frame.loc[i, 'class'] = 'Others;'
        all_class.extend(sub_class_frame.loc[i, 'class'].split(';')[:-1])
    all_class = list(set(all_class))

    n = len(all_class)
    class_count_frame = pd.DataFrame(data=np.zeros((n, n), dtype=int), index=all_class, columns=all_class)
    for i in sub_class_frame.index.values:
        this_class = sub_class_frame.loc[i, 'class'].split(';')[:-1]
        for j in this_class:
            for k in this_class:
                class_count_frame.loc[j, k] += 1
    data = np.array(class_count_frame)

    n_components = 1
    # t_sne = manifold.TSNE(n_components=n_components, init='pca', random_state=0)
    # result = t_sne.fit_transform(data)

    mds = manifold.MDS(n_components=n_components, dissimilarity='precomputed')
    result = mds.fit_transform(data)

    class_loc_frame = pd.DataFrame(index=all_class, columns=['loc'])
    for i in range(len(all_class)):
        class_loc_frame.loc[all_class[i], 'loc'] = result[i][0]
    class_loc_frame.sort_values('loc', inplace=True)

    sorted_class = list(class_loc_frame.index.values)
    class_hpo_array = []
    for i in sorted_class:
        class_hpo_array.append([[], [], []])

    for i in hpo_group:
        this_class_list = sub_class_frame.loc[i, 'class'].split(';')[:-1]
        dis = 10000
        belonged_class = ''
        # 确定该hpo属于哪一类
        for j in this_class_list:
            dis_sum = 0
            for k in this_class_list:
                dis_sum += abs(sorted_class.index(j)-sorted_class.index(k))
            if dis_sum < dis:
                dis = dis_sum
                belonged_class = j
        # 确定该hpo在该类中处于哪边的位置
        judge = 0
        for n in this_class_list:
            if sorted_class.index(n)-sorted_class.index(belonged_class) > 0:
                judge += len(sorted_class) - abs(sorted_class.index(n)-sorted_class.index(belonged_class))
            elif sorted_class.index(n)-sorted_class.index(belonged_class) < 0:
                judge -= len(sorted_class) - abs(sorted_class.index(n)-sorted_class.index(belonged_class))
        if judge == 0:
            class_hpo_array[sorted_class.index(belonged_class)][1].append(i)
        elif judge > 0:
            class_hpo_array[sorted_class.index(belonged_class)][2].append(i)
        else:
            class_hpo_array[sorted_class.index(belonged_class)][0].append(i)

    for i in range(len(class_hpo_array)):
        class_hpo_array[i][0].extend(class_hpo_array[i][1])
        class_hpo_array[i][0].extend(class_hpo_array[i][2])
        class_hpo_array[i] = class_hpo_array[i][0]
    result_str = ''
    for i in range(len(sorted_class)):
        result_str += sorted_class[i]
        result_str += ':'
        result_str += str(len(class_hpo_array[i]))
        result_str += ';'
    result_str += '&&'
    for i in range(len(class_hpo_array)):
        for j in class_hpo_array[i]:
            result_str += j
            result_str += ','
            result_str += str(i)
            result_str += ','
            result_str += sub_class_frame.loc[j, 'class']
            result_str += '|'
    print(result_str)
