import pandas as pd
import numpy as np
from sklearn import manifold
import sys


if __name__ == '__main__':
    hpo_group = list(set(sys.argv[1:]))
    # hpo_group = ['HP:0001250', 'HP:0001249']

    hpo_distance = pd.DataFrame()
    for i in range(11):
        part_distance = pd.read_csv('/Users/yj/IdeaProjects/RD_Map/rd_map/python_code/origin_data/part_dis/part_distance_' + str(i) + '.csv', index_col=0, header=0)
        hpo_distance = pd.concat([hpo_distance, part_distance], axis=1)
    hpo_class = pd.read_csv('/Users/yj/IdeaProjects/RD_Map/rd_map/python_code/origin_data/hpo_class.csv', header=0, index_col=0, encoding='utf8')
    hpo_color = pd.read_csv("/Users/yj/IdeaProjects/RD_Map/rd_map/python_code/origin_data/hpo_color.csv", header=0, index_col=0)

    sub_distance = hpo_distance.loc[hpo_group, hpo_group]
    # sub_distance = hpo_distance.iloc[0:500, 0:500]
    data = np.array(sub_distance)
    column_headers = list(sub_distance.index.values)

    n_components = 1

    tsne = manifold.TSNE(n_components=n_components, init='pca', random_state=0)
    result = tsne.fit_transform(data)  # 转换后的输出
    result1 = []
    for i in result:
        result1.append(round(i[0], 3))
    # print(result1)
    # print(len(result1))
    # print(type(result1[0]))
    # frame = pd.DataFrame(data=result, index=column_headers, columns=['x', 'y'])
    #
    frame = pd.DataFrame(index=column_headers, columns=['loc', 'color', 'class'])
    for i in range(len(column_headers)):
        frame.loc[column_headers[i], 'loc'] = result1[i]

    for i in frame.index.values:
        if pd.isnull(hpo_class.loc[i, 'class']):
            frame.loc[i, 'class'] = '---'
        else:
            frame.loc[i, 'class'] = hpo_class.loc[i, 'class'].replace(';', '|')[:-1]
        frame.loc[i, 'color'] = hpo_color.loc[i, 'color']
    frame.sort_values('loc', inplace=True)
    for i in frame.index.values:
        print(i, frame.loc[i, 'loc'], frame.loc[i, 'color'], frame.loc[i, 'class'],  sep=',', end=';')
