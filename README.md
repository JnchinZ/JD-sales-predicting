**实训说明：**
软件生产实习实训综合题目（15周）
对京东商城的某类产品，选取10种，爬取每个商品近90天的评论数据，并统计每天评论条数，以此计算为销售量。将数据存储为本地文件或存储到数据库后完成以下web页面：

 1. 搜索产品id，显示该种产品的销量变化曲线。

 2. 为了完成积极备货，预测该产品后10天的销售量，预测算法自行选择，此部分可以用python或者数据分析工具预测完毕写入本地数据文件或数据库。搜索产品id，显示该种产品的后10天的销售量。

 3. 统计分析每周的销售量，并用饼图、柱状图显示。

 4. 其他可以分析的功能。

【注】：

 - 本次实训使用mysql数据库；
 - jd_spider.py文件是京东评论区爬虫；
 - predict.py文件是时间序列预测算法（三阶指数平滑算法）的实现；
 - 用爬虫（jd_spider.py）把数据爬取到数据库后，用预测算法（predict.py）进行预测，预测结果转换成json格式数据（数据量太大，最好代码实现，代码太简单，代码内容略），最后用前端技术（demo文件夹）实现演示。