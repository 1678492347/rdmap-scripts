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


def generate_draw_object(frame):
    global draw_data
    global hpo_group
    global node_id
    global orpha_hpo_group
    draw_data['nodes'] = []
    for a_hpo in hpo_group:
        if a_hpo in orpha_hpo_group:
            draw_data['nodes'].append({
                'id': node_id[a_hpo],
                'type': 'phenotype',
                'name': a_hpo,
                'alternate_name': '',
                'label': a_hpo,
                'score': frame.loc[a_hpo, a_hpo],
                'group': 'phenotype',
                'hidden': False,
                'relatedNodeIds': [],
                'relatedLinkIds': []
            })
        else:
            draw_data['nodes'].append({
                'id': node_id[a_hpo],
                'type': 'phenotype',
                'name': a_hpo,
                'alternate_name': '',
                'label': a_hpo,
                'score': 0,
                'group': 'phenotype',
                'hidden': False,
                'relatedNodeIds': [],
                'relatedLinkIds': []
            })
    # for _n in range(len(frame.index.values)):
    #     draw_data['nodes'].append({
    #         'id': _n,
    #         'type': 'phenotype',
    #         'name': frame.index.values[_n],
    #         'alternate_name': '',
    #         'label': frame.index.values[_n],
    #         'score': frame.iloc[_n, _n],
    #         'group': 'phenotype',
    #         'hidden': False,
    #         'relatedNodeIds': [],
    #         'relatedLinkIds': []
    #     })
    draw_data['edges'] = []
    edge_id = 1
    for _n in range(len(frame.index.values)):
        for _m in range(_n+1, len(frame.index.values)):
            if frame.iloc[_n, _m] > 0:
                draw_data['edges'].append({
                    'id': '_' + str(edge_id),
                    'relation': 'co-occurrence',
                    'direction': 'two-way',
                    'source': node_id[frame.index.values[_n]],
                    'target': node_id[frame.index.values[_m]],
                    'score': frame.iloc[_n, _m],
                    'hidden': False,
                    'label': str(frame.iloc[_n, _m]),
                    'from': node_id[frame.index.values[_n]],
                    'to': node_id[frame.index.values[_m]],
                    'sourceType': 'phenotype',
                    'sourceName': frame.index.values[_n],
                    'targetType': 'phenotype',
                    'targetName': frame.index.values[_m]
                })

                draw_data['nodes'][node_id[frame.index.values[_n]]]['relatedNodeIds'].append(node_id[frame.index.values[_m]])
                draw_data['nodes'][node_id[frame.index.values[_n]]]['relatedLinkIds'].append('_' + str(edge_id))
                draw_data['nodes'][node_id[frame.index.values[_m]]]['relatedNodeIds'].append(node_id[frame.index.values[_n]])
                draw_data['nodes'][node_id[frame.index.values[_m]]]['relatedLinkIds'].append('_' + str(edge_id))
                edge_id += 1


def add_not_orpha_node(group):
    global draw_data
    this_id = len(draw_data['nodes'])
    for this_hpo in group:
        draw_data['nodes'].append({
            'id': this_id,
            'type': 'phenotype',
            'name': this_hpo,
            'alternate_name': '',
            'label': this_hpo,
            'score': 0,
            'group': 'phenotype',
            'hidden': False,
            'relatedNodeIds': [],
            'relatedLinkIds': []
        })
        this_id += 1


if __name__ == '__main__':
    t0 = time()
    hpo_group = sys.argv[1:]
    # hpo_group = ['HP:0001252', 'HP:0001276']
    # hpo_group = ['HP:0009073', 'HP:0000297', 'HP:0000508', 'HP:0000602', 'HP:0001315', 'HP:0001256', 'HP:0012716']
    # hpo_group = ['HP:0000297']
    node_id = dict(zip(hpo_group, np.arange(0, len(hpo_group))))

    hpo_index = []
    find_hpo_index()

    orpha_hpo_group = []
    not_orpha_hpo_group = []

    file_index = []
    for hpo in hpo_group:
        is_orpha_hpo = False
        for i in range(len(hpo_index)):
            if hpo in hpo_index[i]:
                file_index.append(i)
                is_orpha_hpo = True
        if is_orpha_hpo:
            orpha_hpo_group.append(hpo)
        else:
            not_orpha_hpo_group.append(hpo)
    file_index = list(set(file_index))

    hpo_relation_score = pd.DataFrame()
    for i in file_index:
        part_hpo_relation_score = pd.read_csv('./origin_data/hpo_relation/hpo_relation_score_' + str(i) + '.csv', index_col=0, header=0)
        convert_part_distance = part_hpo_relation_score.apply(pd.to_numeric, downcast='unsigned')
        hpo_relation_score = pd.concat([hpo_relation_score, part_hpo_relation_score], axis=1)
    draw_data = dict()
    generate_draw_object(hpo_relation_score.loc[orpha_hpo_group, orpha_hpo_group])
    # add_not_orpha_node(not_orpha_hpo_group)
    print(draw_data, end='')

