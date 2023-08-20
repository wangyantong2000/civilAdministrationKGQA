import json
from py2neo import *

from new_new import ner_pre

graph = Graph('http://localhost:7474/', auth=('neo4j', '123456'))

def search_all():
    # 定义data数组，存放节点信息
    data = []
    # 定义关系数组，存放节点间的关系
    links = []
    # 查询所有节点，并将节点信息取出存放在data数组中
    nodes = graph.run('MATCH(n:`组织部门`)-[rel:负责]->(m:`业务`) return n').data()
    node1s = graph.run('MATCH(n:`组织部门`)-[rel:负责]->(m:`业务`) return m').data()
    print(nodes)
    n = {}
    for node in nodes:
        # 将节点信息转化为json格式，否则中文会不显示
        node = json.dumps(node, ensure_ascii=False)
        # 取出节点的name
        node = json.loads(node)
        # 取出节点信息中person的name
        node_name = str(node['n']['name'])
        if (node_name in n.keys() ):
            continue
        n[node_name] = node_name
        # 构造字典，存储单个节点信息
        dict = {
            'name': node_name,
            #'category':0,
            'color': '#afacac',
            'size': 80,

        }
        # 将单个节点信息存放在data数组中
        data.append(dict)
    for node in node1s:
        # 将节点信息转化为json格式，否则中文会不显示
        node = json.dumps(node, ensure_ascii=False)
        # 取出节点的name
        node = json.loads(node)
        # 取出节点信息中person的name
        node_name = str(node['m']['name'])
        if node_name in n.keys():
            continue
        n[node_name] = node_name
        # 构造字典，存储单个节点信息
        dict = {
            'name': node_name,
            #'category': 1,
            'color': '#dbdbdb',
            'size' : 70,

        }
        # 将单个节点信息存放在data数组中
        data.append(dict)
    # 查询所有关系，并将所有的关系信息存放在links数组中
    rps = graph.run('MATCH(n:`组织部门`)-[rel:负责]->(m:`业务`) return rel').data()
    print(rps)
    t = {}
    for r in rps:
        source = str(r['rel'].start_node['name'])
        target = str(r['rel'].end_node['name'])
        if(target in t.keys() and t[target] == source):
            continue
        t[target] = source
        name = str(type(r['rel']).__name__)
        # 构造字典存储单个关系信息
        dict = {
            'source': source,
            'target': target,
            'name': name
        }
        # 将单个关系信息存放进links数组中
        links.append(dict)
    # 将所有的节点信息和关系信息存放在一个字典中
    print(len(links))
    neo4j_data = {
        'data': data,
        'links': links
    }
    #将字典转化json格式
    print(neo4j_data)
    neo4j_data = json.dumps(neo4j_data,ensure_ascii=False)
    return neo4j_data


def search_one(R):
    # 定义data数组存储节点信息
    data = []
    # 定义links数组存储关系信息
    links = []
    nn = {}

    # 查询节点是否存在
    for value in R:
        node = graph.run('MATCH(n{name:"'+value+'"}) return n').data()
        # 如果节点存在len(node)的值为1不存在的话len(node)的值为0
        if len(node) == 0:
            continue
        dict = {
            'name': value,
            'color': '#afacac',
            'size': 70

        }
        if value in nn.keys():
            continue
        nn[value] = value
        data.append(dict)
        # 查询与该节点有关的节点，无向，步长为1，并返回这些节点
        nodes = graph.run('MATCH(n{name:"' + value + '"})<-->(m) return m').data()
        # 查询该节点所涉及的所有relationship，无向，步长为1，并返回这些relationship
        reps = graph.run('MATCH(n{name:"' + value + '"})<-[rel]->(m) return rel').data()
        #查询属性
        property = graph.run('MATCH(n{name:"' + value + '"}) return  properties(n)').data()
        # 处理节点信息
        for n in nodes:
            # 将节点信息的格式转化为json
            node = json.dumps(n, ensure_ascii=False)
            node = json.loads(node)
            # 取出节点信息中person的name
            name = str(node['m']['name'])
            if name in nn.keys():
                continue
            nn[name] = name
            # 构造字典存放单个节点信息
            dict = {
                'name': name,
                #'color': '#28d8a9',
                'color': '#dbdbdb',
                'size' : 60
            }
            # 将单个节点信息存储进data数组中
            data.append(dict)
        # 处理relationship
        for r in reps:
            source = str(r['rel'].start_node['name'])
            target = str(r['rel'].end_node['name'])
            name = str(type(r['rel']).__name__)

            dict = {
                'source': source,
                'target': target,
                'name': name
            }
            links.append(dict)
        # 查询property
        for i in property[0]['properties(n)'].keys():
            if i == 'name':
                continue
            for j in property[0]['properties(n)'][i]:
                source = value
                target = j
                name = i
                dict1 = {
                    'name': target,
                    # 'color': '#28d8a9',
                    'color': '#dbdbdb',
                    'size': 50
                }
                dict = {
                    'source': source,
                    'target': target,
                    'name': name
                }
                data.append(dict1)
                links.append(dict)
    # 构造字典存储data和links
    search_neo4j_data = {
        'data': data,
        'links': links
    }
    if data == []:
        return 0
    # 将dict转化为json格式
    search_neo4j_data = json.dumps(search_neo4j_data,ensure_ascii=False)

    return search_neo4j_data

def searchby(R,pres):
    # 定义data数组存储节点信息
    data = []
    # 定义links数组存储关系信息
    links = []
    nn = {}
    value = list(R)[0]
    press = []

    if ',' in pres:
        pres = pres.split(',')
        for p in pres:
            r = graph.run('MATCH(n{name:"' + value + '"})<-[rel]->(m{name:"' + p + '"}) return rel').data()
            if r != []:
                press.append(p)
    else:
        press.append(pres)
    dict = {
        'name': value,
        'color': '#afacac',#68b758
        'size': 70
    }
    data.append(dict)
    for pre in press:
        pre_label = graph.run('MATCH(n{name:"' + pre + '"}) return labels(n)').data()

        pre_label = pre_label[0]['labels(n)'][0]
        # 查询节点是否存在
        print(pre_label)
        label = graph.run('MATCH(n{name:"' + value + '"}) return labels(n)').data()
        if label==[]:
            return 1
        label = label[0]['labels(n)'][0]
        if pre != value:
            dict = {
                'name': pre,
                'color': '#dbdbdb',#46cba7
                'size': 60
            }
            data.append(dict)
        if label == '业务' and pre_label == '身份':
            # 查询与该节点有关的节点，无向，步长为1，并返回这些节点
            nodes_zz = graph.run('MATCH(n{name:"' + value + '"})<-->(m:组织部门) return m').data()
            pre_nodes_zz = graph.run('MATCH(n{name:"' + pre + '"})<-->(m:组织部门) return m').data()
            tmp_zz = [val for val in nodes_zz if val in pre_nodes_zz]
            nodes_zj = graph.run('MATCH(n{name:"' + value + '"})<-->(m:证件) return m').data()
            pre_nodes_zj = graph.run('MATCH(n{name:"' + pre + '"})<-->(m:证件) return m').data()
            tmp_zj = [val for val in nodes_zj if val in pre_nodes_zj]
            nodes_yw = graph.run('MATCH(n{name:"' + value + '"})<-->(m:业务) return m').data()
            nodes_wp = graph.run('MATCH(n{name:"' + value + '"})<-->(m:物品) return m').data()
            nodes = tmp_zz + tmp_zj + nodes_yw + nodes_wp
        elif label == '身份' and pre_label == '业务':
            # 查询与该节点有关的节点，无向，步长为1，并返回这些节点
            nodes_zz = graph.run('MATCH(n{name:"' + value + '"})<-->(m:组织部门) return m').data()
            pre_nodes_zz = graph.run('MATCH(n{name:"' + pre + '"})<-->(m:组织部门) return m').data()
            tmp_zz = [val for val in nodes_zz if val in pre_nodes_zz]
            nodes_zj = graph.run('MATCH(n{name:"' + value + '"})<-->(m:证件) return m').data()
            pre_nodes_zj = graph.run('MATCH(n{name:"' + pre + '"})<-->(m:证件) return m').data()
            tmp_zj = [val for val in nodes_zj if val in pre_nodes_zj]
            nodes_yiw = graph.run('MATCH(n{name:"' + value + '"})<-->(m:义务) return m').data()
            nodes = tmp_zz + tmp_zj + nodes_yiw
        elif label == '组织部门' and pre_label == '业务':
            # 查询与该节点有关的节点，无向，步长为1，并返回这些节点
            nodes_sf = graph.run('MATCH(n{name:"' + value + '"})<-->(m:身份) return m').data()
            pre_nodes_sf = graph.run('MATCH(n{name:"' + pre + '"})<-->(m:身份) return m').data()
            tmp_sf = [val for val in nodes_sf if val in pre_nodes_sf]
            nodes = tmp_sf
        elif label == '业务' and pre_label == '组织部门':
            # 查询与该节点有关的节点，无向，步长为1，并返回这些节点
            nodes_sf = graph.run('MATCH(n{name:"' + value + '"})<-->(m:身份) return m').data()
            pre_nodes_sf = graph.run('MATCH(n{name:"' + pre + '"})<-->(m:身份) return m').data()
            tmp_sf = [val for val in nodes_sf if val in pre_nodes_sf]
            nodes_yw = graph.run('MATCH(n{name:"' + value + '"})<-->(m:业务) return m').data()
            nodes_wp = graph.run('MATCH(n{name:"' + value + '"})<-->(m:物品) return m').data()
            nodes = tmp_sf + nodes_yw + nodes_wp
        elif label == '身份' and pre_label == '组织部门':
            # 查询与该节点有关的节点，无向，步长为1，并返回这些节点
            nodes_yw = graph.run('MATCH(n{name:"' + value + '"})<-->(m:业务) return m').data()
            pre_nodes_yw = graph.run('MATCH(n{name:"' + pre + '"})<-->(m:业务) return m').data()
            tmp_yw = [val for val in nodes_yw if val in pre_nodes_yw]
            nodes_yiw = graph.run('MATCH(n{name:"' + value + '"})<-->(m:义务) return m').data()
            nodes = tmp_yw + nodes_yiw
        elif label == '组织部门' and pre_label == '身份':
            # 查询与该节点有关的节点，无向，步长为1，并返回这些节点
            nodes_yw = graph.run('MATCH(n{name:"' + value + '"})<-->(m:业务) return m').data()
            pre_nodes_yw = graph.run('MATCH(n{name:"' + pre + '"})<-->(m:业务) return m').data()
            tmp_yw = [val for val in nodes_yw if val in pre_nodes_yw]
            nodes = tmp_yw
        elif label == '证件' and pre_label == '身份':
            # 查询与该节点有关的节点，无向，步长为1，并返回这些节点
            nodes_yw = graph.run('MATCH(n{name:"' + value + '"})<-->(m:业务) return m').data()
            pre_nodes_yw = graph.run('MATCH(n{name:"' + pre + '"})<-->(m:业务) return m').data()
            tmp_yw = [val for val in nodes_yw if val in pre_nodes_yw]
            nodes = tmp_yw
        elif label == '证件' and pre_label == '业务':
            # 查询与该节点有关的节点，无向，步长为1，并返回这些节点
            nodes_sf = graph.run('MATCH(n{name:"' + value + '"})<-->(m:身份) return m').data()
            pre_nodes_sf = graph.run('MATCH(n{name:"' + pre + '"})<-->(m:身份) return m').data()
            tmp_sf = [val for val in nodes_sf if val in pre_nodes_sf]
            nodes = tmp_sf
        elif label == '身份' and pre_label == '证件':
            # 查询与该节点有关的节点，无向，步长为1，并返回这些节点
            nodes_yw = graph.run('MATCH(n{name:"' + value + '"})<-->(m:业务) return m').data()
            pre_nodes_yw = graph.run('MATCH(n{name:"' + pre + '"})<-->(m:业务) return m').data()
            tmp_yw = [val for val in nodes_yw if val in pre_nodes_yw]
            nodes = tmp_yw
        elif label == '业务' and pre_label == '证件':
            # 查询与该节点有关的节点，无向，步长为1，并返回这些节点
            nodes_sf = graph.run('MATCH(n{name:"' + value + '"})<-->(m:身份) return m').data()
            pre_nodes_sf = graph.run('MATCH(n{name:"' + pre + '"})<-->(m:身份) return m').data()
            tmp_sf = [val for val in nodes_sf if val in pre_nodes_sf]
            nodes = tmp_sf
        elif label == '业务' and pre_label == '业务'and pre!=value:
            # 查询与该节点有关的节点，无向，步长为1，并返回这些节点
            nodes_yw = graph.run('MATCH(n{name:"' + value + '"})-->(m:业务) return m').data()
            nodes_zz = graph.run('MATCH(n{name:"' + value + '"})<-->(m:组织部门) return m').data()
            nodes_zj = graph.run('MATCH(n{name:"' + value + '"})<-->(m:证件) return m').data()

            nodes = nodes_yw+nodes_zz+nodes_zj
        else:
            nodes = graph.run('MATCH(n{name:"' + value + '"})<-->(m) return m').data()
        for n in nodes:
            # 将节点信息的格式转化为json
            node = json.dumps(n, ensure_ascii=False)
            node = json.loads(node)
            # 取出节点信息中person的name
            name = str(node['m']['name'])
            if name in nn.keys():
                continue
            nn[name] = name
            # 构造字典存放单个节点信息
            dict = {
                'name': name,
                # 'color': '#28d8a9',
                'color': '#dbdbdb',
                'size': 60
            }
            # 将单个节点信息存储进data数组中
            data.append(dict)
    # 查询该节点所涉及的所有relationship，无向，步长为1，并返回这些relationship
    reps = graph.run('MATCH(n{name:"' + value + '"})<-[rel]->(m) return rel').data()
    #查询属性
    property = graph.run('MATCH(n{name:"' + value + '"}) return  properties(n)').data()
    # 处理节点信息

    # 处理relationship
    for r in reps:
        source = str(r['rel'].start_node['name'])
        target = str(r['rel'].end_node['name'])
        name = str(type(r['rel']).__name__)
        dict = {
            'source': source,
            'target': target,
            'name': name
        }
        links.append(dict)
    # 查询property
    for i in property[0]['properties(n)'].keys():
        if i == 'name':
            continue
        for j in property[0]['properties(n)'][i]:
            source = value
            target = j
            name = i
            dict1 = {
                'name': target,
                # 'color': '#28d8a9',
                'color': '#dbdbdb',
                'size': 50
            }
            dict = {
                'source': source,
                'target': target,
                'name': name
            }
            data.append(dict1)
            links.append(dict)
    # 构造字典存储data和links
    search_neo4j_data = {
        'data': data,
        'links': links
    }
    if data == []:
        return 0
    # 将dict转化为json格式
    search_neo4j_data = json.dumps(search_neo4j_data,ensure_ascii=False)

    return search_neo4j_data
if __name__ == "__main__":
    question = '结婚登记'
    data = []
    # 定义links数组存储关系信息
    links = []
    nn = {}
    t = {}
    yw, sf, zzbm, zj, wp, yiw = ner_pre(question)
    R = set(yw + sf + zzbm + zj + wp + yiw)

    print(11111111)
    print(graph.run('MATCH (n:`业务`{name:"婚姻登记"}) <-[rel]->(m:`业务`{name:"婚姻登记"}) return rel').data())
    pre = '内地居民'
    # 查询节点是否存在
    for value in R:
        label = graph.run('MATCH(n{name:"' + value + '"}) return labels(n)').data()
        label = label[0]['labels(n)'][0]
        pre_label = graph.run('MATCH(n{name:"' + pre + '"}) return labels(n)').data()
        pre_label = pre_label[0]['labels(n)'][0]
        node = graph.run('MATCH(n{name:"' + value + '"}) return n').data()
        # 如果节点存在len(node)的值为1不存在的话len(node)的值为0
        if len(node) == 0:
            continue
        dict = {
            'name': value,
            'color': '#0898f1',
            'size': 50
        }
        data.append(dict)
        if label == '业务' and pre_label == '身份':
            # 查询与该节点有关的节点，无向，步长为1，并返回这些节点
            nodes_zz = graph.run('MATCH(n{name:"' + value + '"})<-->(m:组织部门) return m').data()
            pre_nodes_zz = graph.run('MATCH(n{name:"' + pre + '"})<-->(m:组织部门) return m').data()
            tmp_zz = [val for val in nodes_zz if val in pre_nodes_zz]
            nodes_zj = graph.run('MATCH(n{name:"' + value + '"})<-->(m:证件) return m').data()
            pre_nodes_zj = graph.run('MATCH(n{name:"' + pre + '"})<-->(m:证件) return m').data()
            tmp_zj = [val for val in nodes_zj if val in pre_nodes_zj]
            nodes_yw = graph.run('MATCH(n{name:"' + value + '"})<-->(m:业务) return m').data()
            nodes_wp = graph.run('MATCH(n{name:"' + value + '"})<-->(m:物品) return m').data()
            nodes = tmp_zz + tmp_zj + nodes_yw + nodes_wp
        elif label == '身份' and pre_label == '业务':
            # 查询与该节点有关的节点，无向，步长为1，并返回这些节点
            nodes_zz = graph.run('MATCH(n{name:"' + value + '"})<-->(m:组织部门) return m').data()
            pre_nodes_zz = graph.run('MATCH(n{name:"' + pre + '"})<-->(m:组织部门) return m').data()
            tmp_zz = [val for val in nodes_zz if val in pre_nodes_zz]
            nodes_zj = graph.run('MATCH(n{name:"' + value + '"})<-->(m:证件) return m').data()
            pre_nodes_zj = graph.run('MATCH(n{name:"' + pre + '"})<-->(m:证件) return m').data()
            tmp_zj = [val for val in nodes_zj if val in pre_nodes_zj]
            nodes_yiw = graph.run('MATCH(n{name:"' + value + '"})<-->(m:义务) return m').data()
            nodes = tmp_zz + tmp_zj + nodes_yiw
        elif label == '组织部门' and pre_label == '业务':
            # 查询与该节点有关的节点，无向，步长为1，并返回这些节点
            nodes_sf = graph.run('MATCH(n{name:"' + value + '"})<-->(m:身份) return m').data()
            pre_nodes_sf = graph.run('MATCH(n{name:"' + pre + '"})<-->(m:身份) return m').data()
            tmp_sf = [val for val in nodes_sf if val in pre_nodes_sf]
            nodes = tmp_sf
        elif label == '业务' and pre_label == '组织部门':
            # 查询与该节点有关的节点，无向，步长为1，并返回这些节点
            nodes_sf = graph.run('MATCH(n{name:"' + value + '"})<-->(m:身份) return m').data()
            pre_nodes_sf = graph.run('MATCH(n{name:"' + pre + '"})<-->(m:身份) return m').data()
            tmp_sf = [val for val in nodes_sf if val in pre_nodes_sf]
            nodes_yw = graph.run('MATCH(n{name:"' + value + '"})<-->(m:业务) return m').data()
            nodes_wp = graph.run('MATCH(n{name:"' + value + '"})<-->(m:物品) return m').data()
            nodes = tmp_sf  + nodes_yw + nodes_wp
        elif label == '身份' and pre_label == '组织部门':
            # 查询与该节点有关的节点，无向，步长为1，并返回这些节点
            nodes_yw = graph.run('MATCH(n{name:"' + value + '"})<-->(m:业务) return m').data()
            pre_nodes_yw = graph.run('MATCH(n{name:"' + pre + '"})<-->(m:业务) return m').data()
            tmp_yw = [val for val in nodes_yw if val in pre_nodes_yw]
            nodes_yiw = graph.run('MATCH(n{name:"' + value + '"})<-->(m:义务) return m').data()
            nodes = tmp_yw + nodes_yiw
        elif label == '组织部门' and pre_label == '身份':
            # 查询与该节点有关的节点，无向，步长为1，并返回这些节点
            nodes_yw = graph.run('MATCH(n{name:"' + value + '"})<-->(m:业务) return m').data()
            pre_nodes_yw = graph.run('MATCH(n{name:"' + pre + '"})<-->(m:业务) return m').data()
            tmp_yw = [val for val in nodes_yw if val in pre_nodes_yw]
            nodes = tmp_yw
        else:
            nodes = graph.run('MATCH(n{name:"' + value + '"})<-->(m) return m').data()
        reps = graph.run('MATCH(n{name:"' + value + '"})<-[rel]->(m) return rel').data()
        # 查询属性
        property = graph.run('MATCH(n{name:"' + value + '"}) return  properties(n)').data()






    '''a = search_all()
    b = search_one({'兑现职称待遇'})

    print(b)'''
#村委会换届选举选民法定年龄如何计算？
# 解决 事业单位考取社会工作者职业水平资格的，是否可以兑现职称待遇？ echart点重问题
#语料库索引问题