from elasticsearch import Elasticsearch
import numpy as np
import jieba.posseg as pseg
import gensim
import math

class NerSearch:
    def __init__(self):
        self._index = "ner_data"
        self.es = Elasticsearch([{"host": "127.0.0.1", "port": 9200}])
        self.doc_type = "ner"
        self.embedding_path = r'D:\neo4jtest\minzhengre\sgns.wiki.bin'
        self.embdding_dict = gensim.models.KeyedVectors.load(self.embedding_path, mmap='r')
        self.embedding_size = 300
        self.min_score = 0.4
        self.min_sim = 0.8

    def search_main(self,question):
        # surface_form 为需要匹配的字段。
        query = {'query': {'match': {'ner': question}}}
        es = Elasticsearch([{"host": "127.0.0.1", "port": 9200}])
        es_results = es.search(index='ner_data', doc_type="_doc", size=50, body=query)
        max_score = es_results['hits']['max_score']
        es_results = es_results['hits']['hits']
        # 仅考虑分数最高的候选项。
        # es_results = [es_result for es_result in es_results if es_result['_score'] == max_score]
        es_results = [es_result['_source'] for es_result in es_results]
        if es_results:
            return es_results[0]['ner']
        else:
            return 0
    '''根据question进行事件的匹配查询'''

    def search_specific(self, ner):
        query_body = {
            "query": {
                "match": {
                    'ner': ner,
                }
            }
        }
        searched = self.es.search(index=self._index, doc_type="_doc", body=query_body, size=50)
        # 输出查询到的结果
        return searched["hits"]["hits"]

    '''基于ES的问题查询'''

    def search_es(self, ner):
        answers = []
        res = self.search_specific(ner)
        for hit in res:
            answer_dict = {}
            answer_dict['score'] = hit['_score']
            answer_dict['sim_ner'] = hit['_source']['ner']
            answers.append(answer_dict)
        return answers

    '''对文本进行分词处理'''

    def seg_sent(self, s):
        wds = [i.word for i in pseg.cut(s) if i.flag[0] not in ['x', 'u', 'c', 'p', 'm', 't']]
        return wds

    '''基于wordvector，通过lookup table的方式找到句子的wordvector的表示'''

    def rep_sentencevector(self, sentence, flag='seg'):
        if flag == 'seg':
            word_list = [i for i in sentence.split(' ') if i]
        else:
            word_list = self.seg_sent(sentence)
        embedding = np.zeros(self.embedding_size)
        sent_len = 0
        for index, wd in enumerate(word_list):
            if wd in self.embdding_dict:
                embedding += self.embdding_dict[wd]
                sent_len += 1
            else:
                continue
        return embedding / sent_len

    '''计算问句与库中问句的相似度,对候选结果加以二次筛选'''

    def similarity_cosine(self, vector1, vector2):
        cos1 = np.sum(vector1 * vector2)
        cos21 = np.sqrt(sum(vector1 ** 2))
        cos22 = np.sqrt(sum(vector2 ** 2))
        similarity = cos1 / float(cos21 * cos22)
        if math.isnan(similarity):
            return 0
        else:
            return similarity

    '''问答主函数'''

    def search_main1(self, question):
        candi_answers = self.search_es(question)
        question_vector = self.rep_sentencevector(question,flag='noseg')
        answer_dict = {}
        for indx, candi in enumerate(candi_answers):
            candi_question = candi['sim_ner']
            score = candi['score']/100
            candi_vector = self.rep_sentencevector(candi_question, flag='noseg')
            sim = self.similarity_cosine(question_vector, candi_vector)
            '''if sim < self.min_sim:
                continue'''
            final_score = (score + sim)/2
            '''if final_score < self.min_score:
                continue'''
            answer_dict[indx] = final_score
        if answer_dict:
            answer_dict = sorted(answer_dict.items(), key=lambda asd:asd[1], reverse=True)
            final_answer = candi_answers[answer_dict[0][0]]['sim_ner']
        else:
            final_answer = 0
        return  final_answer


if __name__ == "__main__":
    handler = NerSearch()
    question ='外国的人'

    final_answer = handler.search_main1(question)
    print(final_answer)
