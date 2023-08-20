from py2neo import *
from ner_search import NerSearch
from new_new import ner_pre

handler1 = NerSearch()
graph = Graph("http://localhost", auth=("neo4j", "123456"))
panduan = ['是否', '对吗', '是不是', '？', '吗', '是', '可以']  # 身份、业务、部门；身份、业务、证件
rbm = ['哪', '部门', '地方', '去', '负责']  # 身份、业务->部门
rzj = ['带', '证件', '材料', '需要', '交']  # 身份、业务->证件  部门、业务->证件
rdo = ['如何', '怎么', '想', '办', '进行', '什么']  # 身份、业务->证件、部门
ryw = ['办', '做', '业务', '事情', '什么', '负责']  # 身份、部门->业务 身份->业务
ryiwp = ['拥有', '实现', '应该', '履行', '是', '吗', '对吗', '是不是']  # 身份、义务
ryiwd = ['对谁', '对什么人']  # 身份、义务->身份 对谁
ryiwy = ['被', '由', '来', '什么人','谁对']  # 身份、义务->身份 由谁
rql = ['权利', '权', '享']  # 身份->权利
ryiw = ['实现', '义务']  # 身份->义务
ysf = ['谁', '人', '身份']  # 业务、部门->身份
yzj = ['需', '要', '可不可以', '是否', '是不是']  # 业务、证件
ytj = ['条件', '前提', '为什么']  # 业务->条件
yqj = ['期间', '时候', '时间']  # 业务->期间
yfz = ['法则', '规则', '按照', '原则', '条例', '依据', '标准']  # 业务->法则
ybm = rbm  # 业务->部门
yyw = ['遇到', '之后', '然后', '碰到']  # 业务->业务
ywp = ['物品', '涉及', '关于']  # 业务->物品


def checkword(question, l):
    for wd in l:
        if wd in question:
            return True
    return False


def wd(q, dict):
    flag = False
    ans = ''
    if '身份' in dict.keys():
        if '业务' in dict.keys():
            if '组织部门' in dict.keys() and checkword(q, panduan):
                flag = True
                nodes1 = graph.run('MATCH(n{name:"' + dict['身份'][0] + '"})<-->(m:组织部门) return m').data()
                nodes2 = graph.run('MATCH(n{name:"' + dict['业务'][0] + '"})<-->(m:组织部门) return m').data()
                tmp = [val for val in nodes2 if val in nodes1]
                tmp = [t['m']['name'] for t in tmp]
                if dict['组织部门'][0] in tmp:
                    if ans != '':
                        ans += '<br/>'
                    ans += '对的，' + dict['身份'][0] + '办理' + dict['业务'][0] + '可以去' + dict['组织部门'][0] + '。'
                else:
                    if ans != '':
                        ans += '<br/>'
                    ans += '不，' + dict['身份'][0] + '如果想办理' + dict['业务'][0] + '，可以去' + dict['组织部门'][0] + '；'.join(
                        tmp) + '。'
            if '证件' in dict.keys() and checkword(q, panduan):
                flag = True
                nodes1 = graph.run('MATCH(n{name:"' + dict['身份'][0] + '"})<-->(m:证件) return m').data()
                nodes2 = graph.run('MATCH(n{name:"' + dict['业务'][0] + '"})<-->(m:证件) return m').data()
                tmp = [val for val in nodes2 if val in nodes1]
                tmp = [t['m']['name'] for t in tmp]
                if dict['证件'][0] in tmp:
                    if ans != '':
                        ans += '<br/>'
                    ans += '对的，' + dict['身份'][0] + '办理' + dict['业务'][0] + '需要携带' + dict['证件'][0] + '。'
                else:
                    if ans != '':
                        ans += '<br/>'
                    ans += '不，' + dict['身份'][0] + '如果想办理' + dict['业务'][0] + '，需要携带' + '；'.join(
                        tmp) + '。'
            elif checkword(q, rbm):
                flag = True
                nodes1 = graph.run('MATCH(n{name:"' + dict['身份'][0] + '"})<-->(m:组织部门) return m').data()
                nodes2 = graph.run('MATCH(n{name:"' + dict['业务'][0] + '"})<-->(m:组织部门) return m').data()
                tmp = [val for val in nodes2 if val in nodes1]
                tmp = [t['m']['name'] for t in tmp]
                if tmp:
                    if ans != '':
                        ans += '<br/>'
                    ans += '如果您是' + dict['身份'][0] + '，办理' + dict['业务'][0] + '可以去' + '；'.join(tmp) + '。'
            elif checkword(q, rzj):
                flag = True
                nodes1 = graph.run('MATCH(n{name:"' + dict['身份'][0] + '"})<-->(m:证件) return m').data()
                nodes2 = graph.run('MATCH(n{name:"' + dict['业务'][0] + '"})<-->(m:证件) return m').data()
                tmp = [val for val in nodes2 if val in nodes1]
                tmp = [t['m']['name'] for t in tmp]
                if tmp:
                    if ans != '':
                        ans += '<br/>'
                    ans += '如果您是' + dict['身份'][0] + '，办理' + dict['业务'][0] + '需携带' + '；'.join(tmp) + '。'
            elif checkword(q, rdo):
                flag = True
                nodes1 = graph.run('MATCH(n{name:"' + dict['身份'][0] + '"})<-->(m:组织部门) return m').data()
                nodes2 = graph.run('MATCH(n{name:"' + dict['业务'][0] + '"})<-->(m:组织部门) return m').data()
                tmp1 = [val for val in nodes2 if val in nodes1]
                tmp1 = [t['m']['name'] for t in tmp1]
                nodes3 = graph.run('MATCH(n{name:"' + dict['身份'][0] + '"})<-->(m:证件) return m').data()
                nodes4 = graph.run('MATCH(n{name:"' + dict['业务'][0] + '"})<-->(m:证件) return m').data()
                tmp = [val for val in nodes4 if val in nodes3]
                tmp = [t['m']['name'] for t in tmp]
                if tmp1:
                    if ans != '':
                        ans += '<br/>'
                    ans += '如果您是' + dict['身份'][0] + '，办理' + dict['业务'][0] + '可以去' + '；'.join(tmp1) + '。'
                    if tmp:
                        ans += '并携带' + '；'.join(tmp) + '。'
        elif '组织部门' in dict.keys():
            if checkword(q, ryw):
                flag = True
                nodes1 = graph.run('MATCH(n{name:"' + dict['身份'][0] + '"})<-->(m:业务) return m').data()
                nodes2 = graph.run('MATCH(n{name:"' + dict['组织部门'][0] + '"})<-->(m:业务) return m').data()
                tmp = [val for val in nodes2 if val in nodes1]
                tmp = [t['m']['name'] for t in tmp]
                if tmp:
                    if ans != '':
                        ans += '<br/>'
                    ans += '如果您是' + dict['身份'][0] + '，到' + dict['组织部门'][0] + '可以办理' + '；'.join(tmp) + '。'
        elif '义务' in dict.keys():
            if checkword(q, ryiwy):
                flag = True
                nodes1 = graph.run('MATCH(m)-[name: 实现]->(n{name:"' + dict['义务'][0] + '"}) return m').data()
                tmp = [t['m']['name'] for t in nodes1]
                if tmp:
                    if ans != '':
                        ans += '<br/>'
                    ans += '、'.join(tmp) + '对' + dict['身份'][0] + '有'+ dict['义务'][0] + '的义务。'
            elif checkword(q, ryiwd):
                flag = True
                nodes1 = graph.run('MATCH(m)-[name: 被实现]->(n{name:"' + dict['义务'][0] + '"}) return m').data()
                tmp = [t['m']['name'] for t in nodes1]
                if tmp:
                    if ans != '':
                        ans += '<br/>'
                    ans += '、'.join(tmp) + '对' + dict['身份'][0] + '有' + dict['义务'][0] + '的义务。'
            elif checkword(q, ryiwp):
                flag = True
                nodes1 = graph.run('MATCH(n{name:"' + dict['身份'][0] + '"})-[rel{name:\'实现\'}]->(m:义务) return m').data()
                tmp = [t['m']['name'] for t in nodes1]
                if dict['义务'][0] in tmp:
                    if ans != '':
                        ans += '<br/>'
                    ans += '是的。'+dict['身份'][0]+ '有' + dict['义务'][0] + '的义务。'
                else:
                    if ans != '':
                        ans += '<br/>'
                    ans += '不，'+dict['身份'][0]+'有' + '、'.join(tmp) + '的义务。'
        else:
            if checkword(q, rql):
                flag = True
                property = graph.run('MATCH(n{name:"' + dict['身份'][0] + '"}) return  properties(n)').data()
                property = property[0]['properties(n)']['权利']
                if property:
                    if ans != '':
                        ans += '<br/>'
                    ans += '如果您是' + dict['身份'][0] + ',有' + '、'.join(property) + '的权利。'
            if checkword(q, ryiw):
                flag = True
                nodes1 = graph.run('MATCH(n{name:"' + dict['身份'][0] + '"})-[rel{name:\'实现\'}]->(m:义务) return m').data()
                tmp = [t['m']['name'] for t in nodes1]
                if tmp:
                    if ans != '':
                        ans += '<br/>'
                    ans += '如果您是' + dict['身份'][0]+','
                for t in range(len(tmp)):

                    nodes2 = graph.run('MATCH(m)-[name: 被实现]->(n{name:"' + tmp[t] + '"}) return m').data()
                    tmp1 = [tmp[t]['m']['name'] for tmp[t] in nodes2]
                    if t != len(tmp) - 1:
                        if tmp1:
                            ans += '对' + '、'.join(tmp1) + '有' + tmp[t] + '的义务；'
                        else:
                            ans += '有' + tmp[t] + '的义务；'
                    else:
                        if tmp1:
                            ans += '对' + '、'.join(tmp1) + '有' + tmp[t] + '的义务。'
                        else:
                            ans += '有' + tmp[t] + '的义务。'
            if checkword(q, ryw):
                flag = True
                nodes1 = graph.run('MATCH(n{name:"' + dict['身份'][0] + '"})<-->(m:业务) return m').data()
                tmp = [t['m']['name'] for t in nodes1]
                if tmp:
                    if ans != '':
                        ans += '<br/>'
                    ans += '如果您是' + dict['身份'][0] + ',有' + '；'.join(tmp) + '的权利。'
    elif '业务' in dict.keys():
        if '组织部门' in dict.keys():
            if checkword(q, ysf):
                flag = True
                nodes1 = graph.run('MATCH(n{name:"' + dict['组织部门'][0] + '"})<-->(m:身份) return m').data()
                nodes2 = graph.run('MATCH(n{name:"' + dict['业务'][0] + '"})<-->(m:身份) return m').data()
                tmp = [val for val in nodes2 if val in nodes1]
                tmp = [t['m']['name'] for t in tmp]
                if tmp:
                    if ans != '':
                        ans += '<br/>'
                    ans += '、'.join(tmp)+'可以去'+dict['组织部门'][0]+'办理'+dict['业务'][0]+'。'
            elif checkword(q, rzj):
                flag = True
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
                        flag = True
                        if ans != '':
                            ans += '<br/>'
                        ans += '如果您是'+t + '，到' + dict['组织部门'][0] + '办理' + dict['业务'][0] + '，需携带' + '、'.join(tmp1)+'。'
        elif '证件' in dict.keys():
            if checkword(q, yzj):
                nodes1 = graph.run('MATCH(n{name:"' + dict['业务'][0] + '"})<-->(m:证件) return m').data()
                tmp = [t['m']['name'] for t in nodes1]
                if dict['证件'][0] in tmp:
                    flag = True
                    ans += '是的，'+'办理'+dict['业务'][0]+'需携带'+dict['证件'][0]+'。'
        else:
            if checkword(q, ytj):
                property = graph.run('MATCH(n{name:"' + dict['业务'][0] + '"}) return  properties(n)').data()
                property = property[0]['properties(n)']['条件']
                flag = True
                if property:
                    if ans != '':
                        ans += '<br/>'
                    ans += dict['业务'][0] + '的条件是' + '；'.join(property)  + '。'
            if checkword(q, yqj):
                property = graph.run('MATCH(n{name:"' + dict['业务'][0] + '"}) return  properties(n)').data()
                property = property[0]['properties(n)']['期间']
                flag = True
                if property:
                    if ans != '':
                        ans += '<br/>'
                    ans += dict['业务'][0] + '可以在' + '、'.join(property) +'期间办理'+ '。'
            if checkword(q, yfz):
                property = graph.run('MATCH(n{name:"' + dict['业务'][0] + '"}) return  properties(n)').data()
                property = property[0]['properties(n)']['法则']
                flag = True
                if property:
                    if ans != '':
                        ans += '<br/>'
                    ans += dict['业务'][0] + '按照'+'、'.join(property)+'。'
            if checkword(q, ybm):
                flag = True
                nodes1 = graph.run('MATCH(n{name:"' + dict['业务'][0] + '"})<-->(m:组织部门) return m').data()
                tmp = [t['m']['name'] for t in nodes1]
                if tmp:
                    if ans != '':
                        ans += '<br/>'
                    ans += '、'.join(tmp) + '可以负责' + dict['业务'][0] + '。'
            if checkword(q, yyw):
                flag = True
                nodes1 = graph.run('MATCH(n{name:"' + dict['业务'][0] + '"})-[rel{name:\'进行\'}]->(m:业务) return m').data()
                tmp = [t['m']['name'] for t in nodes1]
                if tmp:
                    if ans != '':
                        ans += '<br/>'
                    ans += '如果您遇到了'+dict['业务'][0] + '，下面需要进行' + '、'.join(tmp) + '。'
            if checkword(q, ywp):
                flag = True
                nodes1 = graph.run('MATCH(n{name:"' + dict['业务'][0] + '"})<-->(m:物品) return m').data()
                tmp = [t['m']['name'] for t in nodes1]
                if tmp:
                    if ans != '':
                        ans += '<br/>'
                    ans += dict['业务'][0] + '涉及到了' + '、'.join(tmp) + '。'
    elif '组织部门' in dict.keys():
        if checkword(q, ryw):
            flag = True
            nodes1 = graph.run('MATCH(n{name:"' + dict['组织部门'][0] + '"})<-->(m:业务) return m').data()
            tmp = [t['m']['name'] for t in nodes1]
            if tmp:
                if ans != '':
                    ans += '<br/>'
                ans += dict['组织部门'][0] + '可以办理' + '、'.join(tmp) + '。'
    if flag == False:
        ans = '好的请继续描述'
    if ans == '':
        ans = '不好意思，这个问题的答案我也不知道。或许换个形式描述试试。'
    if ans !='好的请继续描述' and ans != '不好意思，这个问题的答案我也不知道。或许换个形式描述试试。':
        ans +='<br/>您还有什么问题吗？若问题解决，请输入“结束”结束服务'
    return ans
# 外国人办理婚姻登记是到哪 带啥
