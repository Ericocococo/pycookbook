"""
数据处理 —— 从采集、分析、可视化到存储的完整链路

  01_analysis/       数值计算与表格分析(numpy,后续 pandas)
  02_visualization/  数据可视化(matplotlib / seaborn / plotly 等)
  03_engineering/    数据工程(清洗、ETL、管道、调度)
  04_spider/         数据采集(爬虫、requests、解析)
  05_storage/        数据存储格式(parquet 列式存储等)

适用
  · 结构化/半结构化数据的批处理与分析
  · 量化、报表、特征工程、离线数据管道

不适用
  · 后端 Web 服务 → 07_backend
  · 机器学习建模/训练 → 后续 09_ml(如有)

速查(各子方向典型入口)
  import numpy as np              # 01_analysis 数值计算
  import pandas as pd             # 01_analysis 表格
  df.to_parquet('x.parquet')     # 05_storage 列式存储
"""
