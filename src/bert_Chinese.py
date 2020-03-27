import numpy as np
import json
import torch
from transformers import BertTokenizer, BertModel
from candidate_generation import *
from tqdm import tqdm

class bert_Chinese(object):
    '''
    基于bert中文预训练模型计算POI特征隐向量表示
    基于余弦相似度计算POI相似度，完成POI相似匹配
    '''
    def __init__(self, options=['name', 'type', 'address'], weights=[0.6, 0.2, 0.2]):
        self.options = options
        self.weights = weights
        self.device = torch.device("cuda:3" if torch.cuda.is_available() else "cpu")

    def info_embedding(self, words, max_len):
        '''
        通过bert预训练模型计算POI属性的向量表示
        '''

        # 定义模型
        tokenizer = BertTokenizer.from_pretrained('bert-base-chinese')
        model = BertModel.from_pretrained('bert-base-chinese').to(self.device)

        # 编码单词表
        input_ids = tokenizer.batch_encode_plus(words, add_special_tokens=True, max_length=max_len, pad_to_max_length=True, return_tensors='pt')['input_ids']
        input_ids = input_ids.to(self.device)
        
        # 获得最后一层特征隐向量表示
        outputs = model(input_ids)
        # print(outputs[0].size())
        embeddings = torch.sum(outputs[0], dim=1) / outputs[0].size()[1]
        # print(embeddings.size())

        return embeddings.cpu().detach().numpy()


    def poi_embedding(self, poi_data):
        '''
        获得各个属性的隐向量表示并加权求和，即最终POI向量表示
        '''

        # 逐个属性逐条POI数据计算向量表示
        poi_embeddings = dict()
        for op, w in zip(self.options, self.weights):
            words = []
            max_len = -1
            for p in poi_data:
                
                # 补充缺失属性值
                if p[op] == None or p[op] == []:
                    p[op] = "无"
                words.append(p[op])
                
                # 最长文本长度
                max_len = max(max_len, len(p[op]))
            
            # 对各个属性的特征向量进行加权，可以理解为线性层加权
            poi_embeddings[op] = self.info_embedding(words, max_len) * w
        
        # 所有属性向量加权求和，和上面的加权一起可以理解为一个线性层
        results = []
        for op in self.options:
            if len(results) == 0:
                results = poi_embeddings[op]
            else:
                results += poi_embeddings[op]
        return np.array(results)


    def cos_simlarity(self, word_embedding):
        '''
        计算余弦相似度，內积 / 模的乘积
        '''

        # 计算带匹配POI向量的模，候选POI向量的模
        match_poi_mo = np.linalg.norm(word_embedding[0, :].reshape(1, -1), ord=2, axis=1, keepdims=True)
        candidates_poi_mo = np.linalg.norm(word_embedding[1:, :], ord=2, axis=1, keepdims=True)

        # 內积
        dot_product = np.dot(word_embedding[0, :], word_embedding[1:, :].T)

        # 余弦相似度计算
        cos_sim_matrix = np.array(np.divide(dot_product, (match_poi_mo * candidates_poi_mo).T))
        cos_sim_matrix = cos_sim_matrix.reshape(-1)
        return cos_sim_matrix


    def run(self, input_data, threshold=0.9, filename='../results/bert_chinese.txt'):
        '''
        根据输入的每条POI数据，获取半径一定距离内的候选匹配POI点，根据余弦相似度计算两两相似得分
        根据得分排序，选择得分最高且大于阈值的POI候选点作为匹配结果
        '''

        writer = open(filename, 'w', encoding='utf-8')

        match_results = []
        # 逐条计算与输入POI匹配的点
        for rec in tqdm(input_data[:200]):

            # 候选点获取
            poi_candidates = get_candidates_from_tmap(rec['lng'], rec['lat'])
            poi_candidates.insert(0, rec)

            # POI隐特征向量表示，余弦相似度矩阵计算
            poi_embeddings = self.poi_embedding(poi_candidates)
            cos_sim_matrix = self.cos_simlarity(poi_embeddings)

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
        print(match_results)
        writer.close()
        return  match_results