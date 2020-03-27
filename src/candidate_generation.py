# -*-coding:utf-8-*-
import requests
import math
import time

def coordinates_transformation(lng, lat, ctype=5):
    '''
    用于坐标系转换，不同地图之间的坐标系是不同的
    本Demo中的高德地图和腾讯地图的坐标系是一致的，所以转换结果依然相同
    '''

    # 发送转换坐标的请求
    url = 'https://apis.map.qq.com/ws/coord/v1/translate?locations='+ str(lat) + ',' + str(lng) + '&type=' + str(ctype) + '&key=5BNBZ-WUUL3-PSR34-3VD6C-4AIW3-OCBNK'
    response = requests.get(url)
    coordinates_json = response.json()
    # print(coordinates_json.get('locations')[0])

    # 获取转换后的经纬度坐标
    lng = float(coordinates_json.get('locations')[0]['lng'])
    lat = float(coordinates_json.get('locations')[0]['lat'])
    return lng, lat


def get_candidates_from_tmap(lng, lat, radius=100):
    '''
    根据经纬度坐标获取半径radius米内的POI数据点
    获取的属性主要有id、name、type、address、location等
    '''

    # 坐标转换
    lng, lat = coordinates_transformation(lng, lat)

    # url
    page = 1
    url = 'https://apis.map.qq.com/ws/geocoder/v1/?location='+ str(lat) + ',' + str(lng) + '&key=5BNBZ-WUUL3-PSR34-3VD6C-4AIW3-OCBNK&get_poi=1&poi_options=address_format=short;radius=' + str(radius) + ';page_size=20;page_index=page_id'
    url = url.replace('page_id', str(page))

    # 发送请求，返回页面POI数据(json)
    response = requests.get(url)
    nearby_poi_json = response.json()

    # 获取圆内的候选POI点数量，计算POI点的页面数
    num_nearby_poi = nearby_poi_json.get('result')['poi_count']
    num_page = math.ceil(num_nearby_poi / 20)
    poi_results = []

    # poi_lists = nearby_poi_json.get('result')['pois']
    # if poi_lists != None or '':
    #     for poi in poi_lists:
    #         poi_dict = {}
    #         poi_dict["id"] = poi.get('id')
    #         poi_dict["name"] = poi.get('title')
    #         poi_dict["type"] = poi.get('category')
    #         poi_dict["address"] = poi.get('address')
    #         poi_dict["lng"] = poi.get('location')['lng']
    #         poi_dict["lat"] = poi.get('location')['lat']
    #         # poi_dict["pname"] = poi.get('ad_info')['province']
    #         # poi_dict["cityname"] = poi.get('ad_info')['city']
    #         # poi_dict["adcode"] = poi.get('ad_info')['adcode']
    #         # poi_dict["adname"] = poi.get('ad_info')['district']
    #         poi_dict['distance'] = poi.get('_distance')
    #         poi_results.append(poi_dict)

    # 逐页获取POI数据，返回候选可匹配的POI数据点
    for page in range(1, num_page + 1):
        time.sleep(0.5)
        url = url.replace('page_index=' + str(page-1), 'page_index=' + str(page))
        response = requests.get(url)
        nearby_poi_json = response.json()

        # print(nearby_poi_json)
        poi_lists = nearby_poi_json.get('result')['pois']
        if poi_lists != None or '':
            for poi in poi_lists:
                poi_dict = {}
                poi_dict["id"] = poi.get('id')
                poi_dict["name"] = poi.get('title')
                poi_dict["type"] = poi.get('category')
                poi_dict["address"] = poi.get('address')
                poi_dict["lng"] = poi.get('location')['lng']
                poi_dict["lat"] = poi.get('location')['lat']
                poi_dict['distance'] = poi.get('_distance')
                poi_results.append(poi_dict)

    return poi_results


if __name__=='__main__':
    input_data = read_input()
    for rec in input_data:
        print(rec)
        poi_candidates = get_candidates_from_tmap(rec['lng'], rec['lat'])
        # print(poi_candidates)
