import pandas as pd
import sys
import csv
import numpy as np
from time import time


# 将子节点到父节点的关系存到child2parent_dic
def read_child2parent():
    global child2parent_dic
    term = []
    with open('./origin_data/child2parent.csv', 'r', encoding='UTF-8-sig') as csv_file:
        reader = csv.reader(csv_file)
        relation_list = [row for row in reader]
    this_hpo = relation_list[1][0]
    for a in relation_list[1:]:
        if a[0] == this_hpo:
            term.append(a[1])
        else:
            child2parent_dic[this_hpo] = term
            this_hpo = a[0]
            term = [a[1]]
    child2parent_dic[this_hpo] = term


# 将父节点到子节点的关系存到parent2child_dic
def read_parent2child():
    global parent2child_dic
    term = []
    with open('./origin_data/parent2child.csv', 'r', encoding='UTF-8-sig') as csv_file:
        reader = csv.reader(csv_file)
        relation_list = [row for row in reader]
    this_hpo = relation_list[1][0]
    for a in relation_list[1:]:
        if a[0] == this_hpo:
            term.append(a[1])
        else:
            parent2child_dic[this_hpo] = term
            this_hpo = a[0]
            term = [a[1]]
    parent2child_dic[this_hpo] = term


# 将hpo到根节点到路径存入二维数组
def getParentPath(graph, hpo):
    result = []
    path = [hpo]
    getParentPathDFS(graph, hpo, path, result)
    return result


# DFS向上遍历树
def getParentPathDFS(graph, hpo, path, result):
    if graph[hpo][0] == 'root':
        result.append(path[:])
        return
    for a in graph[hpo]:
        path.append(a)
        getParentPathDFS(graph, a, path, result)
        path.remove(path[-1])
    return


# 将hpo到根节点的dis长度的路径存入二维数组
def getParentPathWithDis(graph, hpo, dis):
    result = []
    path = [hpo]
    getParentPathDFSWithDis(graph, hpo, dis, path, result)
    return result


# DFS向上遍历树，最大长度为dis
def getParentPathDFSWithDis(graph, hpo, dis, path, result):
    if graph[hpo][0] == 'root':
        result.append(path[:])
        return
    if dis == 0:
        result.append(path[:])
        return
    for a in graph[hpo]:
        path.append(a)
        getParentPathDFSWithDis(graph, a, dis - 1, path, result)
        path.remove(path[-1])
    return


# 将hpo到叶子节点到路径存入二维数组
# 谨慎调用，如果hpo层数太低，递归耗时会很久
def getChildrenPath(graph, hpo):
    result = []
    path = [hpo]
    getChildrenPathDFS(graph, hpo, path, result)
    return result


# DFS向下遍历树
def getChildrenPathDFS(graph, hpo, path, result):
    if hpo not in graph.keys():
        result.append(path[:])
        return
    for a in graph[hpo]:
        path.append(a)
        getChildrenPathDFS(graph, a, path, result)
        path.remove(path[-1])
    return


# 将hpo向下dis距离的叶子节点到路径存入二维数组
def getChildrenPathWithDis(graph, hpo, dis):
    result = []
    path = [hpo]
    getChildrenPathDFSWithDis(graph, hpo, dis, path, result)
    return result


# DFS向下遍历树
def getChildrenPathDFSWithDis(graph, hpo, dis, path, result):
    if hpo not in graph.keys():
        result.append(path[:])
        return
    if dis == 0:
        result.append(path[:])
        return
    for a in graph[hpo]:
        path.append(a)
        getChildrenPathDFSWithDis(graph, a, dis - 1, path, result)
        path.remove(path[-1])
    return


def generate_draw_object(frame):
    global draw_data
    global term_set
    global node_id
    global disorder_1
    global hpo2disorder_1
    global disorder_2
    global hpo2disorder_2
    global edge_set
    draw_data['nodes'] = []
    for _n in term_set:
        if _n[:2] == 'HP':
            draw_data['nodes'].append({
                'id': node_id[_n],
                'type': 'phenotype',
                'name': _n,
                'alternate_name': '',
                'label': _n,
                'group': 'phenotype',
                'hidden': False
            })
        else:
            draw_data['nodes'].append({
                'id': node_id[_n],
                'type': 'disease',
                'name': _n,
                'alternate_name': '',
                'label': _n,
                'group': 'phenotype',
                'hidden': False
            })
    draw_data['edges'] = []
    edge_id = 0
    for _n in hpo2disorder_1:
        draw_data['edges'].append({
            'id': '_' + str(edge_id),
            'relation': 'belong_to',
            'direction': 'to',
            'hidden': False,
            'label': 'belong_to',
            'from': node_id[_n],
            'to': node_id[disorder_1],
            'sourceType': 'phenotype',
            'sourceName': _n,
            'targetType': 'disease',
            'targetName': disorder_1
        })
        edge_id += 1
    for _n in hpo2disorder_2:
        draw_data['edges'].append({
            'id': '_' + str(edge_id),
            'relation': 'belong_to',
            'direction': 'to',
            'hidden': False,
            'label': 'belong_to',
            'from': node_id[_n],
            'to': node_id[disorder_2],
            'sourceType': 'phenotype',
            'sourceName': _n,
            'targetType': 'disease',
            'targetName': disorder_2
        })
        edge_id += 1
    for rel in frame:
        for _n in range(len(rel)-1):
            if str(node_id[rel[_n]]) + '-' + str(node_id[rel[_n + 1]]) not in edge_set:
                draw_data['edges'].append({
                    'id': '_' + str(edge_id),
                    'relation': 'is_a',
                    'direction': 'to',
                    'hidden': False,
                    'label': 'is_a',
                    'from': node_id[rel[_n]],
                    'to': node_id[rel[_n + 1]],
                    'sourceType': 'phenotype',
                    'sourceName': rel[_n],
                    'targetType': 'phenotype',
                    'targetName': rel[_n+1]
                })
                edge_id += 1
                edge_set.add(str(node_id[rel[_n]]) + '-' + str(node_id[rel[_n + 1]]))


if __name__ == '__main__':
    # 上下层级距离为2
    hierarchical_dis = 2

    sys_input = sys.argv[1]
    # print(sys_input)
    # sys_input = "entered-hpo=HP:0000003,HP:0000008+887=HP:0002023,HP:0001561,HP:0006703,HP:0002777,HP:0001622,HP:0003422,HP:0002575,HP:0001671,HP:0000104,HP:0000776,HP:0001601,HP:0006501,HP:0030680,HP:0000086,HP:0012732,HP:0000175,HP:0000008,HP:0001195,HP:0005264,HP:0000772,HP:0000048,HP:0001048,HP:0100335,HP:0005107,HP:0000239,HP:0002085,HP:0000028,HP:0001511,HP:0006101,HP:0002323,HP:0000062,HP:0008736,HP:0000126,HP:0001732,HP:0000003,HP:0001177,HP:0005108,HP:0000368,HP:0000047,HP:0001539,HP:0000795+"
    disorders = sys_input.split('+')[:-1]
    # print(disorders)
    # print(len(disorders[0].split('=')[1]))
    # print(len(disorders[1].split('=')[1]))
    # 先处理好，令len(hpo2disorder_1) <= len(hpo2disorder_2):
    if len(disorders[0].split('=')[1]) <= len(disorders[1].split('=')[1]):
        disorder_1 = disorders[0].split('=')[0]
        hpo2disorder_1 = disorders[0].split('=')[1].split(',')
        disorder_2 = disorders[1].split('=')[0]
        hpo2disorder_2 = disorders[1].split('=')[1].split(',')
    else:
        disorder_1 = disorders[1].split('=')[0]
        hpo2disorder_1 = disorders[1].split('=')[1].split(',')
        disorder_2 = disorders[0].split('=')[0]
        hpo2disorder_2 = disorders[0].split('=')[1].split(',')

    # 读取child2parent关系，向上遍历dis长度
    child2parent_dic = dict()
    read_child2parent()

    # 读取parent2child关系，向下遍历dis长度
    parent2child_dic = dict()
    read_parent2child()

    # 从hpo2disorder_1中各个hpo开始，寻找父/子节点，最大深度为2，若父/子节点（不包括本身）在hpo2disorder_2中，记录该关系
    all_relation = []
    for i in hpo2disorder_1:
        this_parent = getParentPathWithDis(child2parent_dic, i, hierarchical_dis)
        for j in this_parent:
            for k in range(1, len(j)):
                if j[k] in hpo2disorder_2:
                    if j[0: k + 1] not in all_relation:
                        all_relation.append(j[0: k + 1])
        this_children = getChildrenPathWithDis(parent2child_dic, i, hierarchical_dis)
        for j in this_children:
            for k in range(1, len(j)):
                if j[k] in hpo2disorder_2:
                    temp = j[0: k + 1]
                    temp.reverse()
                    if temp not in all_relation:
                        all_relation.append(temp)
    # print(all_relation)

    term_set = set()
    term_set.add(disorder_1)
    term_set.add(disorder_2)
    term_set.update(hpo2disorder_1)
    term_set.update(hpo2disorder_2)
    for i in all_relation:
        term_set.update(i)

    node_id = dict(zip(term_set, np.arange(0, len(term_set))))
    # print(node_id)

    draw_data = dict()
    # 对相同的边进行过滤
    edge_set = set()
    generate_draw_object(all_relation)
    print(draw_data, end='')
