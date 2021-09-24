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
    global hpo_set
    global node_id
    global edge_set
    draw_data['nodes'] = []
    for _n in hpo_set:
        draw_data['nodes'].append({
            'id': node_id[_n],
            'type': 'phenotype',
            'name': _n,
            'alternate_name': '',
            'label': _n,
            'group': 'phenotype',
            'hidden': False,
            'relatedNodeIds': [],
            'relatedLinkIds': []
        })
    draw_data['edges'] = []
    edge_id = 0
    for rel in frame:
        for _n in range(len(rel)-1):
            if str(node_id[rel[_n]]) + '-' + str(node_id[rel[_n + 1]]) not in edge_set:
                draw_data['edges'].append({
                    'id': '_' + str(edge_id),
                    'relation': 'is_a',
                    'direction': 'to',
                    'source': node_id[rel[_n]],
                    'target': node_id[rel[_n + 1]],
                    'hidden': False,
                    'label': 'is_a',
                    'from': node_id[rel[_n]],
                    'to': node_id[rel[_n + 1]],
                    'sourceType': 'phenotype',
                    'sourceName': rel[_n],
                    'targetType': 'phenotype',
                    'targetName': rel[_n+1]
                })

                draw_data['nodes'][node_id[rel[_n]]]['relatedNodeIds'].append(node_id[rel[_n+1]])
                draw_data['nodes'][node_id[rel[_n]]]['relatedLinkIds'].append('_' + str(edge_id))
                draw_data['nodes'][node_id[rel[_n+1]]]['relatedNodeIds'].append(node_id[rel[_n]])
                draw_data['nodes'][node_id[rel[_n+1]]]['relatedLinkIds'].append('_' + str(edge_id))
                edge_id += 1
                edge_set.add(str(node_id[rel[_n]]) + '-' + str(node_id[rel[_n + 1]]))


if __name__ == '__main__':
    # 上下层级距离为2
    hierarchical_dis = 2

    start_hpo = sys.argv[1]
    # start_hpo = 'HP:0000008'

    # 读取child2parent关系，向上遍历dis长度
    child2parent_dic = dict()
    read_child2parent()
    this_parent = getParentPathWithDis(child2parent_dic, start_hpo, hierarchical_dis)

    # 读取parent2child关系，向下遍历dis长度
    parent2child_dic = dict()
    read_parent2child()
    this_children = getChildrenPathWithDis(parent2child_dic, start_hpo, hierarchical_dis)
    for i in this_children:
        i.reverse()

    all_relation = this_parent + this_children

    hpo_set = set()
    for i in this_parent:
        hpo_set.update(i)
    for i in this_children:
        hpo_set.update(i)

    node_id = dict(zip(hpo_set, np.arange(0, len(hpo_set))))

    draw_data = dict()
    # 对相同的边进行过滤
    edge_set = set()
    generate_draw_object(all_relation)
    print(draw_data, end='')
