from flask import Flask, render_template, request, jsonify, Response
from model import BertQueryNER
from new_new import ner_pre
from search import *
from ner_search import NerSearch
from chat import wd
app = Flask(__name__)
handler1 = NerSearch()
neo4j_data = search_all()
dict = {}
pre_search={}
@app.route('/')
def hello():
    return render_template('main.html')
@app.route('/index')
def hello_world():  # put application's code here
    return render_template('index.html', neo4j_data=neo4j_data)

@app.route('/worker', methods=['POST', 'GET'])
def search1():
    global pre_search
    if request.method == 'POST':
        result = {}
        question = request.form.get('q')
        result['question'] = question
        yw, sf, zzbm, zj, wp, yiw = ner_pre(question)
        R = set(yw + sf + zzbm + zj + wp + yiw)
        result['ner'] = R
        result['sim_ner'] = set()
        if R:
            answer_ner = []
            for i in R:
                final_ner = handler1.search_main(i)
                if final_ner != 0:
                    answer_ner.append(final_ner)
            if answer_ner != []:
                final_answer_ner = answer_ner
                result['sim_ner'] = set(final_answer_ner)
        else:
            result['search'] = 0
        if result['sim_ner'] != []:
            search_neo4j_data = search_one(result['sim_ner'])
            result['search'] = search_neo4j_data
        return render_template("worker.html", result=result)
    elif request.method == 'GET':
        result = {}
        question = request.args.get('question')
        result['question'] = question
        R = {question}
        result['sim_ner'] = R
        print(request.args.get('pre'))
        if request.args.get('pre'):
            pre = request.args.get('pre')
            search_neo4j_data = searchby(R,pre)
            if search_neo4j_data!=1:
                pre_search = search_neo4j_data
        else:
            search_neo4j_data = search_one(R)
            pre_search = search_neo4j_data
        if search_neo4j_data==1:
            search_neo4j_data = pre_search
            result['question'] = request.args.get('pre')
            R = {request.args.get('pre')}
            result['sim_ner'] = R
        result['search'] = search_neo4j_data

        return render_template("worker.html", result=result)
    else:
        return render_template("worker.html")
@app.route("/chat")
def index():
    dict.clear()
    return render_template("chat.html")
@app.route("/chat1", methods=["POST"])
def chat():
    messages = request.form.get("prompt", None)
    q = json.loads(messages)
    print(q)
    yw, sf, zzbm, zj, wp, yiw = ner_pre(q)
    R = set(yw + sf + zzbm + zj + wp + yiw)
    for i in R:
        final_ner = handler1.search_main(i)
        if final_ner != 0:
            label = graph.run('MATCH(n{name:"' + final_ner + '"}) return labels(n)').data()
            label = label[0]['labels(n)'][0]
            dict[label] = [final_ner]
    ans = wd(q,dict)
    print(dict)
    print(ans)
    return Response(ans, content_type='application/octet-stream')

if __name__ == '__main__':
    #app.run(port=9000)
    app.run(port=8000, debug=True)
# neo4j.bat console
#婚姻登记都有什么业务
#婚姻登记涉及什么法条