import pandas as pd
import sys
import csv
from time import time


# def read_hpo_relation():
#     global hpo_relation_dic
#     term = []
#     with open('/Users/yj/Desktop/all_relation.csv', 'r') as csv_file:
#         reader = csv.reader(csv_file)
#         relation_list = [row for row in reader]
#     this_hpo = relation_list[0][0]
#     for a in relation_list:
#         if a[0] == this_hpo:
#             a = [x for x in a if x != '']
#             term.append(a)
#         else:
#             hpo_relation_dic[this_hpo] = term
#             this_hpo = a[0]
#             a = [x for x in a if x != '']
#             term = [a]
#     hpo_relation_dic[this_hpo] = term


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


# # 将父节点到子节点的关系存到parent2child_dic
# def read_parent2child():
#     global parent2child_dic
#     term = []
#     with open('/Users/yj/Desktop/parent2child.csv', 'r', encoding='UTF-8-sig') as csv_file:
#         reader = csv.reader(csv_file)
#         relation_list = [row for row in reader]
#     this_hpo = relation_list[1][0]
#     for a in relation_list[1:]:
#         if a[0] == this_hpo:
#             term.append(a[1])
#         else:
#             parent2child_dic[this_hpo] = term
#             this_hpo = a[0]
#             term = [a[1]]
#     parent2child_dic[this_hpo] = term


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
    for i in graph[hpo]:
        path.append(i)
        getParentPathDFS(graph, i, path, result)
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
    for i in graph[hpo]:
        path.append(i)
        getChildrenPathDFS(graph, i, path, result)
        path.remove(path[-1])
    return


# 返回两个表型的is_a关系路径
def getRelationPathOfHPOs(graph, hpo1, hpo2):
    result = []
    path = [hpo1]
    getRelationPathOfHPOsDFS(graph, hpo1, hpo2, path, result)
    if len(result) == 0:
        path = [hpo2]
        getRelationPathOfHPOsDFS(graph, hpo2, hpo1, path, result)
    return result


# 在hpo1进行DFS搜索hpo2
def getRelationPathOfHPOsDFS(graph, hpo1, hpo2, path, result):
    if hpo1 == hpo2:
        result.append(path[:])
        return
    if (hpo1 not in graph.keys()) or (graph[hpo1][0] == 'root'):
        return
    for i in graph[hpo1]:
        path.append(i)
        getRelationPathOfHPOsDFS(graph, i, hpo2, path, result)
        path.remove(path[-1])
    return


# 查找两个hpo的最近公共祖先并计算距离
# 输入为两个hpo到root到路径
def getLCA(term1, term2):
    result = []
    for _i in term1:
        for _j in term2:
            ancestors = list(set(_i) & set(_j))
            for _k in ancestors:
                distance1 = _i.index(_k) + _j.index(_k)
                result.append([_k, distance1])
    lca = result[1][:]
    for _i in result:
        if _i[1] < lca[1]:
            lca[0] = _i[0]
            lca[1] = _i[1]
    return lca


if __name__ == '__main__':

    child2parent_dic = dict()
    read_child2parent()

    # 针对一个表型，能映射到人体图（判断表型到root的路径）
    # 需要做额外处理的有
    # "HP:0002087": "Abnormality of the upper respiratory tract" 修改人体图中的标签
    # "HP:0000153": "Abnormality of the mouth" 修改人体图中的标签
    # "HP:0003549": "Abnormality of connective tissue" 人体图中添加结缔组织
    # "HP:0025031": "Abnormality of the digestive system" 映射到人体图中的胃部异常
    # "HP:0000119": "Abnormality of the genitourinary system" 映射到人体图中的男女
    # "HP:0001574": "Abnormality of the integument" 映射到人体图中的皮肤异常
    # "HP:0040064": "Abnormality of limbs" 映射到人体图中的上肢+下肢
    hpo_body_map = {"HP:0000478": "Abnormality of the eye", "HP:0000152": "Abnormality of head and neck",
                    "HP:0000707": "Abnormality of the nervous system", "HP:0000598": "Abnormality of the ear",
                    "HP:0000366": "Abnormality of the nose", "HP:0000153": "Abnormality of the mouth",
                    "HP:0002087": "Abnormality of the upper respiratory tract", "HP:0001608": "Abnormality of the voice",
                    "HP:0001871": "Abnormality of blood and blood-forming tissues", "HP:0001626": "Abnormality of the cardiovascular system",
                    "HP:0002086": "Abnormality of the respiratory system", "HP:0000769": "Abnormality of the breast",
                    "HP:0003011": "Abnormality of the musculature", "HP:0000924": "Abnormality of the skeletal system",
                    "HP:0003549": "Abnormality of connective tissue", "HP:0001392": "Abnormality of the liver",
                    "HP:0025031": "Abnormality of the digestive system", "HP:0000077": "Abnormality of the kidney",
                    "HP:0002250": "Abnormality of the large intestine", "HP:0002244": "Abnormality of the small intestine",
                    "HP:0000119": "Abnormality of the genitourinary system", "HP:0001574": "Abnormality of the integument",
                    "HP:0001155": "Abnormality of the hand", "HP:0000834": "Abnormality of the adrenal glands",
                    "HP:0001732": "Abnormality of the pancreas", "HP:0001743": "Abnormality of the spleen",
                    "HP:0040064": "Abnormality of limbs", "HP:0002817": "Abnormality of the upper limb",
                    "HP:0002814": "Abnormality of the lower limb"}


    # 针对一组表型，能映射到人体图（判断表型到root的路径）
    hpo_group = sys.argv[1:]
    # hpo_group = ['HP:0009073', 'HP:0000297', 'HP:0000508', 'HP:0000602', 'HP:0001315', 'HP:0001256']
    body_score_map = dict.fromkeys(hpo_body_map.keys(), 0)
    # print(body_score_map)
    for hpo in hpo_group:
        class_set = set()
        for i in getParentPath(child2parent_dic, hpo):
            for j in i:
                class_set.add(j)
        for i in class_set:
            if i in body_score_map.keys():
                body_score_map[i] += 1
    print(body_score_map, end='')
