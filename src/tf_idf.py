import jieba
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.pipeline import make_pipeline
import numpy as np
from candidate_generation import *
import json

class TF_IDF(object):
    '''
    基于TF-IDF编码向量，SVD降维得到POI向量表示
    基于余弦相似度计算POI相似度，完成POI相似匹配
    '''
    def __init__(self, options=['name', 'type', 'address'], weights=[3, 1, 1]):
        self.options = options
        self.weights = weights

    def word_list(self, input_data):
        '''
        将POI对应属性的文本进行分词，通过词频调整权重，获得词表
        '''
        result = []

        # 对每条输入POI进行jieba分词
        for sample in input_data:
            temp_word_list = []
            # print(sample)
            for op, w in zip(self.options, self.weights):
                # 判断对应属性是否为空
                if sample[op] == None or sample[op] == []:
                    continue
                
                segmentation = list(jieba.cut(sample[op], cut_all=True)) * w
                temp_word_list.extend(segmentation)
            
            # 所有分词结果组成词表
            result.append(' '.join(temp_word_list))
        return result


    def tfidf_svd(self, words, stop_word=[',', '。', '(', ')', ':', '!', ';', '-', '\''], k=10):
        '''
        构建TF-IDF模型，SVD降维，可以理解为LSA模型，获得词向量表示(POI向量)
        '''

        # 模型定义
        vectorizer = TfidfVectorizer(token_pattern='(?u)\\b\\w+\\b', ngram_range=(1, 2), sublinear_tf=True, use_idf=True)
        svd = TruncatedSVD(n_components=k)
        lsa = make_pipeline(vectorizer, svd)

        # 模型学习
        model = lsa.fit(words)

        # 获得词向量表示
        word_embedding = np.matrix(model.transform(words))
        return word_embedding


    def cos_simlarity(self, word_embedding):
        '''
        计算余弦相似度，內积 / 模的乘积
        '''

        # 计算带匹配POI向量的模，候选POI向量的模
        match_poi_mo = np.linalg.norm(word_embedding[0, :], ord=2, axis=1, keepdims=True)
        candidates_poi_mo = np.linalg.norm(word_embedding[1:, :], ord=2, axis=1, keepdims=True)

        # 內积
        dot_product = np.dot(word_embedding[0, :], word_embedding[1:, :].T)

        # 余弦相似度计算
        cos_sim_matrix = np.array(np.divide(dot_product, (match_poi_mo * candidates_poi_mo).T))
        cos_sim_matrix = cos_sim_matrix.reshape(-1)
        return cos_sim_matrix


    def run(self, input_data, threshold=0.3, filename='../results/tfidf_svd.txt'):
        '''
        根据输入的每条POI数据，获取半径一定距离内的候选匹配POI点，根据余弦相似度计算两两相似得分
        根据得分排序，选择得分最高且大于阈值的POI候选点作为匹配结果
        '''
        writer = open(filename, 'w', encoding='utf-8')

        match_results = []
        # 逐条计算与输入POI匹配的点
        for rec in input_data[:200]:

            # 候选点获取
            poi_candidates = get_candidates_from_tmap(rec['lng'], rec['lat'])
            poi_candidates.insert(0, rec)

            # 分词词表，POI词向量表示，余弦相似度矩阵计算
            words = self.word_list(poi_candidates)
            word_embedding = self.tfidf_svd(words)
            cos_sim_matrix = self.cos_simlarity(word_embedding)

            # 选择余弦相似度最大的POI点，且要求大于阈值，否则不算匹配到
            id = np.argmax(cos_sim_matrix)
            # print(cos_sim_matrix)
            if cos_sim_matrix[id] > threshold:
                print(rec['id'], rec['name'])
                print(poi_candidates[id + 1]['id'], poi_candidates[id + 1]['name'])
                print()
                match_results.append([rec, poi_candidates[id + 1]])
                writer.write(json.dumps(rec) + '\t' + json.dumps(poi_candidates[id]) + '\n')
            else:
                print(rec['id'], rec['name'])
                print('None')
                print()
                match_results.append(([rec]))
                writer.write(json.dumps(rec) + '\n')
        # print(match_results)
        writer.close()
        return  match_results