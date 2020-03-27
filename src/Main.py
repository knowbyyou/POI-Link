from edit_distance import Edit_Distance
from tf_idf import TF_IDF
from bert_Chinese import bert_Chinese
import json

def read_input(filename='../poi_data/amap.txt'):
    raw_data = []
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f.readlines():
            raw_data.append(json.loads(line))
    input_data = []
    for d in raw_data:
        rec = dict()
        rec['id'] = d['id']
        rec['name'] = d['name']
        rec['type'] = d['type']
        rec['address'] = d['address']
        rec['lng'] = float(d['location'].split(',')[0])
        rec['lat'] = float(d['location'].split(',')[1])
        input_data.append(rec)
    return input_data

if __name__=='__main__':
    input_data = read_input()

    # 基于编辑距离
    # edit_distance_model = Edit_Distance()
    # edit_distance_model.run(input_data)

    # 基于TF-IDF结合SVD
    # tfidf_svd_model = TF_IDF()
    # tfidf_svd_model.run(input_data)

    # # 基于bert-Chinese
    bert_chinese_model = bert_Chinese()
    bert_chinese_model.run(input_data)