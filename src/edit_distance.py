from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from candidate_generation import *
import json

class Edit_Distance(object):
    '''
    基于编辑距离计算相似度，完成POI相似匹配
    选用名称、类型和地址三个属性来进行文本编辑距离的计算，并根据不同属性赋予不同的权重获得最终得分
    '''
    def __init__(self, options=['name', 'type', 'address'], weights=[0.6, 0.2, 0.2]):
        self.options = options
        self.weights = weights


    def str_distance_score(self, str1, str2):
        '''
        计算字符串之间的编辑距离
        '''

        # 不考虑符号顺序的编辑距离得分
        return fuzz.token_sort_ratio(str1, str2)


    def poi_distance_score(self, amap_poi, tmap_poi):
        '''
        根据POI不同属性的编辑距离得分，加权求和得到最终的相似度得分
        '''

        score = 0.0    
        # 加权求和得分
        for op, w in zip(self.options, self.weights):
            score += w * self.str_distance_score(amap_poi[op], tmap_poi[op])
        
        return score


    def run(self, input_data, threshold=70, filename='../results/edit_distance_match.txt'):
        '''
        根据输入的每条POI数据，获取半径一定距离内的候选匹配POI点，根据编辑距离计算两两相似得分
        根据得分排序，选择得分最高且大于阈值的POI候选点作为匹配结果
        '''
        writer = open(filename, 'w', encoding='utf-8')

        match_results = []
        # 逐条计算与输入POI匹配的点
        for rec in input_data[:200]:

            # 候选点获取
            poi_candidates = get_candidates_from_tmap(rec['lng'], rec['lat'])
            
            # 每条候选与当前查询POI点计算编辑距离得分
            candidates_score = []
            for c in poi_candidates:
                candidates_score.append(self.poi_distance_score(rec, c))
            # print(candidates_score)

            # 选择得分最大的POI点，且要求大于阈值，否则不算匹配到
            if (max(candidates_score) > threshold):
                id = candidates_score.index(max(candidates_score))
                print(rec['id'], rec['name'])
                print(poi_candidates[id]['id'], poi_candidates[id]['name'])
                print()
                match_results.append([rec, poi_candidates[id]])
                writer.write(json.dumps(rec) + '\t' + json.dumps(poi_candidates[id]) + '\n')
            else:
                print(rec['id'], rec['name'])
                print('None')
                print()
                match_results.append(([rec]))
                writer.write(json.dumps(rec) + '\n')
            # input()
        # print(match_results)
        writer.close()
        return match_results
