from py2neo import *
from ner_search import NerSearch
from new_new import ner_pre
handler1 = NerSearch()
graph = Graph("http://localhost", auth=("neo4j", "123456"))
w = "请输入你的信息，输入”结束“结束对话\n"
dict = {}
panduan = ['是否', '对吗', '是不是', '？', '吗', '是', '可以']  # 身份、业务、部门；身份、业务、证件
rbm = ['哪', '部门', '地方', '去', '负责']  # 身份、业务->部门
rzj = ['带', '证件', '材料', '需要', '提交']  # 身份、业务->证件  部门、业务->证件
rdo = ['如何', '怎么', '想', '办', '进行', '什么']  # 身份、业务->证件、部门
ryw = ['办', '做', '业务', '事情', '什么', '负责']  # 身份、部门->业务 身份->业务
ryiwp = ['拥有', '实现', '应该', '履行', '是', '吗', '对吗', '是不是']  # 身份、义务
ryiwd = ['对谁', '对什么人', '谁']  # 身份、义务->身份 对谁
ryiwy = ['被', '由', '来', '什么人']  # 身份、义务->身份 由谁
rql = ['权利', '权', '享']# 身份->权利
ryiw = ['实现', '义务']# 身份->义务
ysf = ['谁','人','身份']#业务、部门->身份
yzj =['需','要','可不可以','是否','是不是']#业务、证件
ytj = ['条件','前提','为什么']#业务->条件
yqj = ['期间','时候','时间']#业务->期间
yfz = ['法则','规则','按照','原则','条例','依据','标准']#业务->法则
ybm = rbm #业务->部门
yyw = ['遇到','之后','然后','怎么','做','办']#业务->业务
ywp = ['物品','涉及','关于']#业务->物品
def checkword(question, l):
    for wd in l:
        if wd in question:
            return True
    return False

while True:
    q = input(w)
    if q == '结束':
        break
    yw, sf, zzbm, zj, wp, yiw = ner_pre(q)
    R = set(yw + sf + zzbm + zj + wp + yiw)
    for i in R:
        final_ner = handler1.search_main(i)
        if final_ner != 0:
            label = graph.run('MATCH(n{name:"' + final_ner + '"}) return labels(n)').data()
            label = label[0]['labels(n)'][0]
            if label not in dict.keys():
                dict[label] = [final_ner]
            else:
                dict[label].append(final_ner)
    print(dict)
    flag = False
    if '身份' in dict.keys():
        if '业务' in dict.keys():
            if '组织部门' in dict.keys() and checkword(q, panduan):
                nodes1 = graph.run('MATCH(n{name:"' + dict['身份'][0] + '"})<-->(m:组织部门) return m').data()
                nodes2 = graph.run('MATCH(n{name:"' + dict['业务'][0] + '"})<-->(m:组织部门) return m').data()
                tmp = [val for val in nodes2 if val in nodes1]
                tmp = [t['m']['name'] for t in tmp]
                if dict['组织部门'][0] in tmp:
                    print('对')
                else:
                    print('、'.join(tmp))
            elif '证件' in dict.keys() and checkword(q, panduan):
                nodes1 = graph.run('MATCH(n{name:"' + dict['身份'][0] + '"})<-->(m:证件) return m').data()
                nodes2 = graph.run('MATCH(n{name:"' + dict['业务'][0] + '"})<-->(m:证件) return m').data()
                tmp = [val for val in nodes2 if val in nodes1]
                tmp = [t['m']['name'] for t in tmp]
                if dict['证件'][0] in tmp:
                    print('对')
                else:
                    print('、'.join(tmp))
            else:
                if checkword(q, rbm):
                    nodes1 = graph.run('MATCH(n{name:"' + dict['身份'][0] + '"})<-->(m:组织部门) return m').data()
                    nodes2 = graph.run('MATCH(n{name:"' + dict['业务'][0] + '"})<-->(m:组织部门) return m').data()
                    tmp = [val for val in nodes2 if val in nodes1]
                    tmp = [t['m']['name'] for t in tmp]
                    print('、'.join(tmp))
                elif checkword(q, rzj):
                    nodes1 = graph.run('MATCH(n{name:"' + dict['身份'][0] + '"})<-->(m:证件) return m').data()
                    nodes2 = graph.run('MATCH(n{name:"' + dict['业务'][0] + '"})<-->(m:证件) return m').data()
                    tmp = [val for val in nodes2 if val in nodes1]
                    tmp = [t['m']['name'] for t in tmp]
                    print('、'.join(tmp))
                elif checkword(q, rdo):
                    nodes1 = graph.run('MATCH(n{name:"' + dict['身份'][0] + '"})<-->(m:组织部门) return m').data()
                    nodes2 = graph.run('MATCH(n{name:"' + dict['业务'][0] + '"})<-->(m:组织部门) return m').data()
                    tmp1 = [val for val in nodes2 if val in nodes1]
                    tmp1 = [t['m']['name'] for t in tmp1]
                    print('、'.join(tmp1))
                    nodes3 = graph.run('MATCH(n{name:"' + dict['身份'][0] + '"})<-->(m:证件) return m').data()
                    nodes4 = graph.run('MATCH(n{name:"' + dict['业务'][0] + '"})<-->(m:证件) return m').data()
                    tmp = [val for val in nodes4 if val in nodes3]
                    tmp = [t['m']['name'] for t in tmp]
                    print('、'.join(tmp))
        elif '组织部门' in dict.keys():
            if checkword(q, ryw):
                nodes1 = graph.run('MATCH(n{name:"' + dict['身份'][0] + '"})<-->(m:业务) return m').data()
                nodes2 = graph.run('MATCH(n{name:"' + dict['组织部门'][0] + '"})<-->(m:业务) return m').data()
                tmp = [val for val in nodes2 if val in nodes1]
                tmp = [t['m']['name'] for t in tmp]
                print('、'.join(tmp))
        elif '义务' in dict.keys():
            if checkword(q, ryiwy):
                nodes1 = graph.run('MATCH(m)-[name: 实现]->(n{name:"' + dict['义务'][0] + '"}) return m').data()
                tmp = [t['m']['name'] for t in nodes1]
                print('、'.join(tmp))
            elif checkword(q, ryiwd):
                nodes1 = graph.run('MATCH(m)-[name: 被实现]->(n{name:"' + dict['义务'][0] + '"}) return m').data()
                tmp = [t['m']['name'] for t in nodes1]
                print('、'.join(tmp))
            elif checkword(q, ryiwp):
                nodes1 = graph.run('MATCH(n{name:"' + dict['身份'][0] + '"})-[rel{name:\'实现\'}]->(m:义务) return m').data()
                tmp = [t['m']['name'] for t in nodes1]
                if dict['义务'][0] in tmp:
                    print('dui')
                else:
                    print('fou')
        else:
            if checkword(q, rql):
                property = graph.run('MATCH(n{name:"' + dict['身份'][0] + '"}) return  properties(n)').data()
                property = property[0]['properties(n)']['权利']
                print('、'.join(property))
            if checkword(q, ryiw):
                nodes1 = graph.run('MATCH(n{name:"' + dict['身份'][0] + '"})-[rel{name:\'实现\'}]->(m:义务) return m').data()
                tmp = [t['m']['name'] for t in nodes1]
                for t in tmp:
                    nodes2 = graph.run('MATCH(m)-[name: 被实现]->(n{name:"' + t + '"}) return m').data()
                    tmp1 = [t['m']['name'] for t in nodes2]
                    if tmp1:
                        print(dict['身份'][0]+'对'+'、'.join(tmp1)+'有'+t+'的义务')
            if checkword(q, ryw):
                nodes1 = graph.run('MATCH(n{name:"' + dict['身份'][0] + '"})<-->(m:业务) return m').data()
                tmp = [t['m']['name'] for t in nodes1]
                print('、'.join(tmp))
    if '业务' in dict.keys():
        if '组织部门' in dict.keys():
            if checkword(q, ysf):
                nodes1 = graph.run('MATCH(n{name:"' + dict['组织部门'][0] + '"})<-->(m:身份) return m').data()
                nodes2 = graph.run('MATCH(n{name:"' + dict['业务'][0] + '"})<-->(m:身份) return m').data()
                tmp = [val for val in nodes2 if val in nodes1]
                tmp = [t['m']['name'] for t in tmp]
                print('、'.join(tmp))
            elif checkword(q,rzj):
                nodes1 = graph.run('MATCH(n{name:"' + dict['组织部门'][0] + '"})<-->(m:身份) return m').data()
                nodes2 = graph.run('MATCH(n{name:"' + dict['业务'][0] + '"})<-->(m:身份) return m').data()
                tmp = [val for val in nodes2 if val in nodes1]
                tmp = [t['m']['name'] for t in tmp]
                nodes3 = graph.run('MATCH(n{name:"' + dict['业务'][0] + '"})<-->(m:证件) return m').data()
                for t in tmp:
                    nodes4 = graph.run('MATCH(n{name:"' + t + '"})<-->(m:证件) return m').data()
                    tmp1 = [val for val in nodes4 if val in nodes3]
                    tmp1 = [t['m']['name'] for t in tmp1]
                    if tmp1:
                        print(t+'到'+dict['组织部门'][0]+'办理'+dict['业务'][0]+'需携带'+'、'.join(tmp1))
        elif '证件' in dict.keys():
            if checkword(q, zj):
                nodes1 = graph.run('MATCH(n{name:"' + dict['业务'][0] + '"})<-->(m:证件) return m').data()
                tmp = [t['m']['name'] for t in nodes1]
                if dict['证件'][0] in tmp:
                    print('dui')
        else:
            if checkword(q, ytj):
                property = graph.run('MATCH(n{name:"' + dict['业务'][0] + '"}) return  properties(n)').data()
                property = property[0]['properties(n)']['条件']
                print('、'.join(property))
            if checkword(q, yqj):
                property = graph.run('MATCH(n{name:"' + dict['业务'][0] + '"}) return  properties(n)').data()
                property = property[0]['properties(n)']['期间']
                print('、'.join(property))
            if checkword(q, yfz):
                property = graph.run('MATCH(n{name:"' + dict['业务'][0] + '"}) return  properties(n)').data()
                property = property[0]['properties(n)']['法则']
                print('、'.join(property))
            if checkword(q, ybm):
                nodes1 = graph.run('MATCH(n{name:"' + dict['业务'][0] + '"})<-->(m:组织部门) return m').data()
                tmp = [t['m']['name'] for t in nodes1]
                print('、'.join(tmp))
            if checkword(q, yyw):
                nodes1 = graph.run('MATCH(n{name:"' + dict['业务'][0] + '"})-[rel{name:\'进行\'}]->(m:业务) return m').data()
                tmp = [t['m']['name'] for t in nodes1]
                print('、'.join(tmp))
            if checkword(q, ywp):
                nodes1 = graph.run('MATCH(n{name:"' + dict['业务'][0] + '"})<-->(m:物品) return m').data()
                tmp = [t['m']['name'] for t in nodes1]
                print('、'.join(tmp))
    if '组织部门' in dict.keys():
        if checkword(q, ryw):
            nodes1 = graph.run('MATCH(n{name:"' + dict['组织部门'][0] + '"})<-->(m:业务) return m').data()
            tmp = [t['m']['name'] for t in nodes1]
            print('、'.join(tmp))
    if flag == False:
        print('好的请继续描述')
# 外国人结婚登记是到内地居民常住户口所在地的婚姻登记机关

