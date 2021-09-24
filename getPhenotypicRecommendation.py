import pandas as pd
import sys
import csv
import json
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


def find_hpo_index():
    global hpo_index
    with open('./origin_data/hpo_relation/hpo_relation_score_index.csv', 'r') as file:
        reader = csv.reader(file)
        rows = [row for row in reader]
        for a in rows:
            hpo_index.append(a)


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

    sys_input = sys.argv[1]
    hpo_group = sys_input.split('+')[0].split(',')
    # hpo_group = 'HP:0009073,HP:0000297,HP:0000508,HP:0000602,HP:0001315,HP:0001256'.split(',')
    # aaa = "{\"top_n\":30,\"data\":{\"HP:0000508\":24,\"HP:0001249\":18,\"HP:0001250\":16,\"HP:0001252\":16,\"HP:0001251\":13,\"HP:0001324\":11,\"HP:0001288\":11,\"HP:0002015\":10,\"HP:0000218\":9,\"HP:0002650\":9,\"HP:0003198\":9,\"HP:0009830\":9,\"HP:0010628\":9,\"HP:0002093\":9,\"HP:0003202\":9,\"HP:0001284\":9,\"HP:0003236\":8,\"HP:0001265\":8,\"HP:0001263\":8,\"HP:0000639\":8,\"HP:0000597\":8,\"HP:0000602\":8,\"HP:0002515\":8,\"HP:0001270\":8,\"HP:0003307\":7,\"HP:0000505\":7,\"HP:0001315\":7,\"HP:0000648\":7,\"HP:0003458\":7,\"HP:0003691\":7,\"HP:0003388\":7,\"HP:0001260\":7,\"HP:0002376\":6,\"HP:0001639\":6,\"HP:0000496\":6,\"HP:0000518\":6,\"HP:0001337\":6,\"HP:0000407\":6,\"HP:0001347\":6,\"HP:0003457\":6,\"HP:0004322\":6,\"HP:0003701\":5,\"HP:0001332\":5,\"HP:0000716\":5,\"HP:0002421\":5,\"HP:0001618\":5,\"HP:0003200\":5,\"HP:0001508\":5,\"HP:0000298\":5,\"HP:0003324\":5,\"HP:0002167\":5,\"HP:0001290\":5,\"HP:0000544\":5,\"HP:0003306\":5,\"HP:0000739\":4,\"HP:0002747\":4,\"HP:0002119\":4,\"HP:0000252\":4,\"HP:0040083\":4,\"HP:0008064\":4,\"HP:0002804\":4,\"HP:0003326\":4,\"HP:0001388\":4,\"HP:0001612\":4,\"HP:0002033\":4,\"HP:0002205\":4,\"HP:0011968\":4,\"HP:0002067\":4,\"HP:0002020\":4,\"HP:0002875\":4,\"HP:0003403\":4,\"HP:0000750\":4,\"HP:0000276\":4,\"HP:0004326\":4,\"HP:0003803\":4,\"HP:0100543\":4,\"HP:0001276\":4,\"HP:0001561\":4,\"HP:0001762\":4,\"HP:0001761\":4,\"HP:0100295\":4,\"HP:0002355\":4,\"HP:0000767\":4,\"HP:0007256\":4,\"HP:0002486\":4,\"HP:0001645\":4,\"HP:0001387\":4,\"HP:0002808\":4,\"HP:0000651\":4,\"HP:0001374\":3,\"HP:0002092\":3,\"HP:0002120\":3,\"HP:0002104\":3,\"HP:0002460\":3,\"HP:0002751\":3,\"HP:0002910\":3,\"HP:0000821\":3,\"HP:0001644\":3,\"HP:0002329\":3,\"HP:0000822\":3,\"HP:0002063\":3,\"HP:0007018\":3,\"HP:0002027\":3,\"HP:0002151\":3,\"HP:0001257\":3,\"HP:0001558\":3,\"HP:0012378\":3,\"HP:0000467\":3,\"HP:0010864\":3,\"HP:0007703\":3,\"HP:0002360\":3,\"HP:0012722\":3,\"HP:0002169\":3,\"HP:0003323\":3,\"HP:0003551\":3,\"HP:0003401\":3,\"HP:0010535\":3,\"HP:0000961\":3,\"HP:0002072\":3,\"HP:0003128\":3,\"HP:0001283\":3,\"HP:0002019\":3,\"HP:0011675\":3,\"HP:0003737\":3,\"HP:0000912\":3,\"HP:0000470\":3,\"HP:0003273\":3,\"HP:0003394\":3,\"HP:0002017\":3,\"HP:0002359\":3,\"HP:0002987\":3,\"HP:0000708\":3,\"HP:0000768\":3,\"HP:0001763\":3,\"HP:0000565\":3,\"HP:0011807\":3,\"HP:0001903\":3,\"HP:0000411\":3,\"HP:0003325\":3,\"HP:0000369\":3,\"HP:0000762\":3,\"HP:0003473\":3,\"HP:0003690\":3,\"HP:0001678\":3,\"HP:0000365\":3,\"HP:0001522\":2,\"HP:0001621\":2,\"HP:0009053\":2,\"HP:0001638\":2,\"HP:0010508\":2,\"HP:0010307\":2,\"HP:0002652\":2,\"HP:0001744\":2,\"HP:0001760\":2,\"HP:0002514\":2,\"HP:0012332\":2,\"HP:0004889\":2,\"HP:0007178\":2,\"HP:0011398\":2,\"HP:0012801\":2,\"HP:0002445\":2,\"HP:0030208\":2,\"HP:0025401\":2,\"HP:0005930\":2,\"HP:0002392\":2,\"HP:0030842\":2,\"HP:0100285\":2,\"HP:0008443\":2,\"HP:0003712\":2,\"HP:0004885\":2,\"HP:0011469\":2,\"HP:0002872\":2,\"HP:0005943\":2,\"HP:0000478\":2,\"HP:0001611\":2,\"HP:0000504\":2,\"HP:0003693\":2,\"HP:0000308\":2,\"HP:0000568\":2,\"HP:0002870\":2,\"HP:0010536\":2,\"HP:0002073\":2,\"HP:0000712\":2,\"HP:0003546\":2,\"HP:0002500\":2,\"HP:0002396\":2,\"HP:0001272\":2,\"HP:0003688\":2,\"HP:0000819\":2,\"HP:0100022\":2,\"HP:0002240\":2,\"HP:0000238\":2,\"HP:0030237\":2,\"HP:0002490\":2,\"HP:0000580\":2,\"HP:0001328\":2,\"HP:0000543\":2,\"HP:0003477\":2,\"HP:0000256\":2,\"HP:0012103\":2,\"HP:0003547\":2,\"HP:0000338\":2,\"HP:0001824\":2,\"HP:0010553\":2,\"HP:0002013\":2,\"HP:0001712\":2,\"HP:0001349\":2,\"HP:0001256\":2,\"HP:0000193\":2,\"HP:0009046\":2,\"HP:0003391\":2,\"HP:0000980\":2,\"HP:0002353\":2,\"HP:0002882\":2,\"HP:0001999\":2,\"HP:0001510\":2,\"HP:0002071\":2,\"HP:0002878\":2,\"HP:0001336\":2,\"HP:0000028\":2,\"HP:0006380\":2,\"HP:0002792\":2,\"HP:0000975\":2,\"HP:0001274\":2,\"HP:0003687\":2,\"HP:0004661\":2,\"HP:0002024\":2,\"HP:0008872\":2,\"HP:0006785\":2,\"HP:0010978\":2,\"HP:0100576\":2,\"HP:0100613\":2,\"HP:0000316\":2,\"HP:0001771\":2,\"HP:0002155\":2,\"HP:0000160\":2,\"HP:0000175\":2,\"HP:0000093\":2,\"HP:0000662\":2,\"HP:0000738\":2,\"HP:0004631\":2,\"HP:0002076\":2,\"HP:0001513\":2,\"HP:0002230\":2,\"HP:0002269\":2,\"HP:0002354\":2,\"HP:0000853\":2,\"HP:0002578\":2,\"HP:0000836\":2,\"HP:0002750\":2,\"HP:0100716\":2,\"HP:0003443\":2,\"HP:0000347\":2,\"HP:0005155\":2,\"HP:0030117\":2,\"HP:0003141\":2,\"HP:0001605\":2,\"HP:0009125\":2,\"HP:0003418\":2,\"HP:0008994\":2,\"HP:0005115\":2,\"HP:0000939\":2,\"HP:0008997\":2,\"HP:0000482\":2,\"HP:0003805\":2,\"HP:0008956\":2,\"HP:0008948\":2,\"HP:0000545\":2,\"HP:0000486\":2,\"HP:0000083\":2,\"HP:0031374\":1,\"HP:0000124\":1,\"HP:0007020\":1,\"HP:0001262\":1,\"HP:0001410\":1,\"HP:0001994\":1,\"HP:0040291\":1,\"HP:0008972\":1,\"HP:0007133\":1,\"HP:0006980\":1,\"HP:0030211\":1,\"HP:0031108\":1,\"HP:0002783\":1,\"HP:0001941\":1,\"HP:0001488\":1,\"HP:0002928\":1,\"HP:0002415\":1,\"HP:0030195\":1,\"HP:0001285\":1,\"HP:0012379\":1,\"HP:0030203\":1,\"HP:0008619\":1,\"HP:0006555\":1,\"HP:0003436\":1,\"HP:0003398\":1,\"HP:0003109\":1,\"HP:0003076\":1,\"HP:0002643\":1,\"HP:0003355\":1,\"HP:0002098\":1,\"HP:0002791\":1,\"HP:0009028\":1,\"HP:0002465\":1,\"HP:0100275\":1,\"HP:0007240\":1,\"HP:0007221\":1,\"HP:0002464\":1,\"HP:0000571\":1,\"HP:0000303\":1,\"HP:0002136\":1,\"HP:0002075\":1,\"HP:0000666\":1,\"HP:0001583\":1,\"HP:0001667\":1,\"HP:0003554\":1,\"HP:0001310\":1,\"HP:0006251\":1,\"HP:0012246\":1,\"HP:0000207\":1,\"HP:0000657\":1,\"HP:0002938\":1,\"HP:0000221\":1,\"HP:0001371\":1,\"HP:0100301\":1,\"HP:0030205\":1,\"HP:0030202\":1,\"HP:0002815\":1,\"HP:0030191\":1,\"HP:0003327\":1,\"HP:0005216\":1,\"HP:0007941\":1,\"HP:0000512\":1,\"HP:0006951\":1,\"HP:0003487\":1,\"HP:0002828\":1,\"HP:0002301\":1,\"HP:0008736\":1,\"HP:0001608\":1,\"HP:0000135\":1,\"HP:0100021\":1,\"HP:0001518\":1,\"HP:0008936\":1,\"HP:0005968\":1,\"HP:0002509\":1,\"HP:0000366\":1,\"HP:0000612\":1,\"HP:0000358\":1,\"HP:0000551\":1,\"HP:0000718\":1,\"HP:0001376\":1,\"HP:0000286\":1,\"HP:0008002\":1,\"HP:0007730\":1,\"HP:0006824\":1,\"HP:0001730\":1,\"HP:0001291\":1,\"HP:0000873\":1,\"HP:0000771\":1,\"HP:0000176\":1,\"HP:0007957\":1,\"HP:0040081\":1,\"HP:0001460\":1,\"HP:0002126\":1,\"HP:0012400\":1,\"HP:0002334\":1,\"HP:0002536\":1,\"HP:0003560\":1,\"HP:0007973\":1,\"HP:0007731\":1,\"HP:0001339\":1,\"HP:0045040\":1,\"HP:0001331\":1,\"HP:0001305\":1,\"HP:0000528\":1,\"HP:0000541\":1,\"HP:0000556\":1,\"HP:0000587\":1,\"HP:0000501\":1,\"HP:0001302\":1,\"HP:0001321\":1,\"HP:0007227\":1,\"HP:0002018\":1,\"HP:0002014\":1,\"HP:0002922\":1,\"HP:0003348\":1,\"HP:0009077\":1,\"HP:0005659\":1,\"HP:0003387\":1,\"HP:0002194\":1,\"HP:0003431\":1,\"HP:0003448\":1,\"HP:0001155\":1,\"HP:0025149\":1,\"HP:0030196\":1,\"HP:0002352\":1,\"HP:0002579\":1,\"HP:0003270\":1,\"HP:0012764\":1,\"HP:0004396\":1,\"HP:0007141\":1,\"HP:0012515\":1,\"HP:0012850\":1,\"HP:0002091\":1,\"HP:0410011\":1,\"HP:0011024\":1,\"HP:0000044\":1,\"HP:0000815\":1,\"HP:0001394\":1,\"HP:0001403\":1,\"HP:0002099\":1,\"HP:0002094\":1,\"HP:0003199\":1,\"HP:0025461\":1,\"HP:0003720\":1,\"HP:0100749\":1,\"HP:0030199\":1,\"HP:0007108\":1,\"HP:0009005\":1,\"HP:0008049\":1,\"HP:0003722\":1,\"HP:0003484\":1,\"HP:0009027\":1,\"HP:0003402\":1,\"HP:0001446\":1,\"HP:0000726\":1,\"HP:0003011\":1,\"HP:0000534\":1,\"HP:0000581\":1,\"HP:0000600\":1,\"HP:0000643\":1,\"HP:0000689\":1,\"HP:0000737\":1,\"HP:0000772\":1,\"HP:0000787\":1,\"HP:0000926\":1,\"HP:0000944\":1,\"HP:0000426\":1,\"HP:0000396\":1,\"HP:0000023\":1,\"HP:0000069\":1,\"HP:0000079\":1,\"HP:0000205\":1,\"HP:0000211\":1,\"HP:0000232\":1,\"HP:0000293\":1,\"HP:0000294\":1,\"HP:0000343\":1,\"HP:0000368\":1,\"HP:0001083\":1,\"HP:0001239\":1,\"HP:0003042\":1,\"HP:0003044\":1,\"HP:0003179\":1,\"HP:0004325\":1,\"HP:0005830\":1,\"HP:0006487\":1,\"HP:0007740\":1,\"HP:0008056\":1,\"HP:0008734\":1,\"HP:0009743\":1,\"HP:0002983\":1,\"HP:0002857\":1,\"HP:0001385\":1,\"HP:0001537\":1,\"HP:0001557\":1,\"HP:0001601\":1,\"HP:0001620\":1,\"HP:0002410\":1,\"HP:0002047\":1,\"HP:0002645\":1,\"HP:0002673\":1,\"HP:0002812\":1,\"HP:0011001\":1,\"HP:0002816\":1,\"HP:0000091\":1,\"HP:0001053\":1,\"HP:0001103\":1,\"HP:0001123\":1,\"HP:0001635\":1,\"HP:0001716\":1,\"HP:0004942\":1,\"HP:0001733\":1,\"HP:0001945\":1,\"HP:0001969\":1,\"HP:0002039\":1,\"HP:0001012\":1,\"HP:0000830\":1,\"HP:0000100\":1,\"HP:0000164\":1,\"HP:0000212\":1,\"HP:0000377\":1,\"HP:0000649\":1,\"HP:0000670\":1,\"HP:0000717\":1,\"HP:0000725\":1,\"HP:0000823\":1,\"HP:0000829\":1,\"HP:0002069\":1,\"HP:0002150\":1,\"HP:0007360\":1,\"HP:0007420\":1,\"HP:0008207\":1,\"HP:0002615\":1,\"HP:0012377\":1,\"HP:0002607\":1,\"HP:0100646\":1,\"HP:0100651\":1,\"HP:0100820\":1,\"HP:0001259\":1,\"HP:0005978\":1,\"HP:0005214\":1,\"HP:0002204\":1,\"HP:0002381\":1,\"HP:0002401\":1,\"HP:0002637\":1,\"HP:0002647\":1,\"HP:0100729\":1,\"HP:0100247\":1,\"HP:0003287\":1,\"HP:0007481\":1,\"HP:0004372\":1,\"HP:0002251\":1,\"HP:0011069\":1,\"HP:0001541\":1,\"HP:0012086\":1,\"HP:0100660\":1,\"HP:0003390\":1,\"HP:0000479\":1,\"HP:0002059\":1,\"HP:0002345\":1,\"HP:0002362\":1,\"HP:0002548\":1,\"HP:0002921\":1,\"HP:0002936\":1,\"HP:0010808\":1,\"HP:0010526\":1,\"HP:0001877\":1,\"HP:0001892\":1,\"HP:0001927\":1,\"HP:0002310\":1,\"HP:0002633\":1,\"HP:0002716\":1,\"HP:0003110\":1,\"HP:0006554\":1,\"HP:0008955\":1,\"HP:0008959\":1,\"HP:0003552\":1,\"HP:0007641\":1,\"HP:0000017\":1,\"HP:0000969\":1,\"HP:0001392\":1,\"HP:0001946\":1,\"HP:0001962\":1,\"HP:0003438\":1,\"HP:0007302\":1,\"HP:0100704\":1,\"HP:0007183\":1,\"HP:0000998\":1,\"HP:0012664\":1,\"HP:0007042\":1,\"HP:0025403\":1,\"HP:0100653\":1,\"HP:0001952\":1,\"HP:0001254\":1,\"HP:0002066\":1,\"HP:0002375\":1,\"HP:0002322\":1,\"HP:0003731\":1,\"HP:0004308\":1,\"HP:0005110\":1,\"HP:0001629\":1,\"HP:0000820\":1,\"HP:0012368\":1,\"HP:0001939\":1,\"HP:0002164\":1,\"HP:0004374\":1,\"HP:0010049\":1,\"HP:0001048\":1,\"HP:0002357\":1,\"HP:0002346\":1,\"HP:0004887\":1,\"HP:0000278\":1,\"HP:0003700\":1,\"HP:0001765\":1,\"HP:0002383\":1,\"HP:0012544\":1,\"HP:0100569\":1,\"HP:0100612\":1,\"HP:0100795\":1,\"HP:0100813\":1,\"HP:0000458\":1,\"HP:0000488\":1,\"HP:0000529\":1,\"HP:0000958\":1,\"HP:0000616\":1,\"HP:0002045\":1,\"HP:0001654\":1,\"HP:0000711\":1,\"HP:0000713\":1,\"HP:0000826\":1,\"HP:0001266\":1,\"HP:0002487\":1,\"HP:0002521\":1,\"HP:0002527\":1,\"HP:0003781\":1,\"HP:0003719\":1,\"HP:0100732\":1,\"HP:0002179\":1,\"HP:0012785\":1,\"HP:0002007\":1,\"HP:0100807\":1,\"HP:0001355\":1,\"HP:0006466\":1,\"HP:0008180\":1,\"HP:0010804\":1,\"HP:0000938\":1,\"HP:0030192\":1,\"HP:0002089\":1,\"HP:0008981\":1,\"HP:0000183\":1}}"
    # top_n_disease_hpo_dic = json.loads(aaa)
    # print(sys_input.split('+')[1])
    top_n_disease_hpo_dic = {'top_n': int(sys_input.split('+')[1].split('top_n:')[1].split(',data')[0])}
    data_dic = {}
    for i in sys_input.split('+')[1].split('data:')[1].split(','):
        key = 'HP:' + i.split(':')[1]
        data_dic[key] = int(i.split(':')[2])
    top_n_disease_hpo_dic['data'] = data_dic
    top_n_disease_hpo = list(top_n_disease_hpo_dic['data'].keys())  # A
    # 共现topn
    cooccur_top_n = 100
    # 上下层级距离为2
    hierarchical_dis = 2

    # 读取child2parent关系，向上遍历dis长度
    child2parent_dic = dict()
    read_child2parent()

    # 读取parent2child关系，向下遍历dis长度
    parent2child_dic = dict()
    read_parent2child()

    # 获取共现特征矩阵
    hpo_index = []
    find_hpo_index()
    file_index = []

    orpha_hpo_group = []
    not_orpha_hpo_group = []
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
        part_hpo_relation_score = pd.read_csv(
            './origin_data/hpo_relation/hpo_relation_score_' + str(
                i) + '.csv', index_col=0, header=0)
        convert_part_distance = part_hpo_relation_score.apply(pd.to_numeric, downcast='unsigned')
        hpo_relation_score = pd.concat([hpo_relation_score, part_hpo_relation_score], axis=1)
    # # print(hpo_relation_score)
    # this_hpo_score = hpo_relation_score[this_hpo[0]].nlargest(100)
    # # this_hpo_score = this_hpo_score.sort_values(ascending=False)
    # this_hpo_score = this_hpo_score[this_hpo_score > 0]

    result_dic = {}

    for this_hpo in hpo_group:
        # getHierarchicalHpos # B
        # getCooccurrentHpos # C
        # A&B A&C A&B&C
        this_parent = getParentPathWithDis(child2parent_dic, this_hpo, hierarchical_dis)
        this_children = getChildrenPathWithDis(parent2child_dic, this_hpo, hierarchical_dis)
        hierarchical_hpo_set = set()
        for i in this_parent:
            hierarchical_hpo_set.update(i)
        for i in this_children:
            hierarchical_hpo_set.update(i)
        hierarchical_hpo_set.difference_update(hpo_group)   # B
        hierarchical_hpo_set.intersection_update(top_n_disease_hpo)     # A&B

        cooccurrent_hpo_set = set()
        if this_hpo in orpha_hpo_group:
            cooccurrent_hpo_series = hpo_relation_score[this_hpo].nlargest(cooccur_top_n)
            cooccurrent_hpo_set.update(cooccurrent_hpo_series.index.values)
            cooccurrent_hpo_set.difference_update(hpo_group)    # C
            cooccurrent_hpo_set.intersection_update(top_n_disease_hpo)      # A&C

        hierarchical_cooccurrent_hpo_set = hierarchical_hpo_set.intersection(cooccurrent_hpo_set)     # A&B&C

        all_hpo_set = hierarchical_hpo_set | cooccurrent_hpo_set  # A&B|A&C
        for hpo in all_hpo_set:

            hpo_value = result_dic.get(hpo, [[], [], [], 0])

            if hpo not in hierarchical_hpo_set:
                # cooccurrent_hpo
                hpo_value[1].append(this_hpo)
                # cooccurrent_hpo_score
                hpo_value[2].append(str(cooccurrent_hpo_series[hpo]) + '/' + str(cooccurrent_hpo_series[this_hpo]))
                hpo_value[3] += 1
                hpo_value[3] += round(cooccurrent_hpo_series[hpo] / cooccurrent_hpo_series[this_hpo] / 100, 4)
            elif hpo not in cooccurrent_hpo_set:
                # hierarchical_hpo
                hpo_value[0].append(this_hpo)
                hpo_value[3] += 2
                hpo_value[3] += round(top_n_disease_hpo_dic['data'][hpo] / top_n_disease_hpo_dic['top_n'], 2)
            else:
                # hierarchical_hpo
                hpo_value[0].append(this_hpo)
                # cooccurrent_hpo
                hpo_value[1].append(this_hpo)
                # cooccurrent_hpo_score
                hpo_value[2].append(str(cooccurrent_hpo_series[hpo]) + '/' + str(cooccurrent_hpo_series[this_hpo]))
                hpo_value[3] += 3
            result_dic[hpo] = hpo_value

    print(result_dic, end='')
