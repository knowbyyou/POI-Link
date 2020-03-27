# -*-coding:utf-8-*-
import requests
import math
import time
import json

def get_poi(amap_url, writer, page_size=20):
    '''
    根据输入的url(POI类型)来获取对应类型的POI数据，并写入文件
    获取的属性主要有id、name、type、address、location等
    '''

    # url
    page = 1
    url = amap_url.replace('page_size', str(page_size))
    url = url.replace('page_index', str(page))

    # 发送请求，返回页面POI数据(json)
    response = requests.get(url)
    poi_json = response.json()

    # 获取当前类型POI数据的页面数
    num_record = int(poi_json.get('count', 0))
    num_page = math.ceil(num_record / page_size)

    poi_results = []
    time.sleep(0.5)
    # poi_set = dict()
    
    # 逐页获取POI数据，并写入文件
    for page in range(1, num_page + 1):
        url = url.replace('page=' + str(page-1), 'page=' + str(page))
        # print(url)
        response = requests.get(url)
        poi_json = response.json()
        poi_lists = poi_json.get('pois')
        if poi_lists != None or '':
            for poi in poi_lists:
                poi_dict = {}
                poi_dict["id"] = poi.get('id')
                poi_dict["biz_type"] = poi.get('biz_type')
                poi_dict["name"] = poi.get('name')
                poi_dict["type"] = poi.get('type')
                poi_dict["address"] = poi.get('address')
                poi_dict["tel"] = poi.get('tel')
                poi_dict["location"] = poi.get('location')
                poi_dict["pcode"] = poi.get('pcode')
                poi_dict["pname"] = poi.get('pname')
                poi_dict["citycode"] = poi.get('citycode')
                poi_dict["cityname"] = poi.get('cityname')
                poi_dict["adcode"] = poi.get('adcode')
                poi_dict["adname"] = poi.get('adname')
                poi_dict["business_area"] = poi.get('business_area')

                # if poi_dict["id"] not in poi_set.keys():
                #     poi_set[poi_dict["id"]] = True
                # else:
                #     continue

                poi_str = json.dumps(poi_dict)
                writer.write(poi_str + '\n')
                poi_results.append(poi_dict)
        time.sleep(0.5)
    return poi_results


if __name__=='__main__':

    # 高德地图POI数据的类型，这里采用的都是大类
    poi_types = ['010000', '020000', '030000', '040000', '050000', '060000', \
                 '070000', '080000', '090000', '100000', '110000', '120000', \
                 '130000', '140000', '150000', '160000', '170000', '180000', \
                 '190000', '200000', '220000', '970000', '990000']

    writer = open('../poi_data/amap.txt', 'w', encoding='utf-8')
    cnt = 0

    # 逐类型获取高德地图POI数据
    for t in poi_types:
        url = 'http://restapi.amap.com/v3/place/text?key=9904da6afe5c8a474ca4018cb48152c3&types=' + t + '&city=shenzhen&citylimit=true&children=1&offset=page_size&page=page_index&extensions=all'
        print('获取POI: ' + t + '... ...')
        poi_results = get_poi(url, writer)
        cnt += len(poi_results)
        print('获取'+ t + '类型POI完成。共：' + str(len(poi_results)) + '条。')
    
    print(cnt)
    writer.close()

    # with open('../poi_data/amap.txt', 'r', encoding='utf-8') as f:
    #     for line in f.readlines():
    #         print(json.loads(line)['id'], json.loads(line)['name'])