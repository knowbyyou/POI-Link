# POI-Link
A Demo that is used to map the POIs of amap to tmap.  

说明：本Demo以三种方式实现了由高德地图到腾讯地图的POI数据点的匹配，分别是**基于字符串相似度的方式（编辑距离）、基于主题模型的方式（TF-IDF&TruncatedSVD）、基于深度学习的方式（Bert中文预训练模型）**。  

src：源码，Main.py为程序入口；  
results：匹配后的结果输出；  
poi_data：由高德地图api获取的POI数据。  

运行方式：python Main.py
