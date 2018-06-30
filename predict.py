import pymysql
import pandas as pd
import operator
import datetime
import matplotlib.pyplot as plt
from  collections import Counter


def get_list():
    #数据库连接
    db = pymysql.connect("localhost", "root", "5531239", "TESTDB", charset='utf8')
    cursor = db.cursor()

    # 查找获取数据库内容
    sql = "select comment_date from item12010266"
    cursor.execute(sql)
    result = []
    result = cursor.fetchall()

    #数据统一格式 'yyyy-mm-dd'
    result = [i[0] for i in result]
    # print(result)
    result = [i[:10] for i in result]
    # print(result)

    #数据按照时间排序
    result.sort()

    #统计相同时间出现的次数
    results = Counter(result)
    # print(results)
    # print(result)
    # print(len(results))
    resultList = [0 for i in range(len(results))]

    #做一张对照表，从开始时间到终止时间的所有天数
    datelist = []
    start = result[0]
    end = result[-1]
    datestart = datetime.datetime.strptime(start, '%Y-%m-%d')
    dateend = datetime.datetime.strptime(end, '%Y-%m-%d')
    while datestart < dateend:
        datestart += datetime.timedelta(days=1)
        datelist.append(str(datestart)[0:10])
    # print(datelist)
    # print (type(datelist[1]))

    #获取一个按照时间排列的词频表
    resultLis = []
    for i in range(len(datelist)):
        if results[datelist[i]]:
            # print(datelist[i], " ", results[datelist[i]])
            resultLis.append(results[datelist[i]])
        else:
            resultLis.append(0)
            # print(result[i],":",results[result[i]])
    resultLis=resultLis[-90:]
    return resultLis

#指数平滑算法
def exponential_smoothing(alpha, s):
    '''
    一次指数平滑
    :param alpha:  平滑系数
    :param s:      数据序列， list
    :return:       返回一次指数平滑模型参数， list
    '''
    s_temp = [0 for i in range(len(s))]
    s_temp[0] = ( s[0] + s[1] + s[2] ) / 3
    for i in range(1, len(s)):
        s_temp[i] = alpha * s[i] + (1 - alpha) * s_temp[i-1]
    return s_temp

def compute_single(alpha, s):
    '''
    一次指数平滑
    :param alpha:  平滑系数
    :param s:      数据序列， list
    :return:       返回一次指数平滑模型参数， list
    '''
    return exponential_smoothing(alpha, s)

def compute_double(alpha, s):
    '''
    二次指数平滑
    :param alpha:  平滑系数
    :param s:      数据序列， list
    :return:       返回二次指数平滑模型参数a, b， list
    '''
    s_single = compute_single(alpha, s)
    s_double = compute_single(alpha, s_single)

    a_double = [0 for i in range(len(s))]
    b_double = [0 for i in range(len(s))]

    for i in range(len(s)):
        a_double[i] = 2 * s_single[i] - s_double[i]                    #计算二次指数平滑的a
        b_double[i] = (alpha / (1 - alpha)) * (s_single[i] - s_double[i])  #计算二次指数平滑的b

    return a_double, b_double

def compute_triple(alpha, s):
    '''
    三次指数平滑
    :param alpha:  平滑系数
    :param s:      数据序列， list
    :return:       返回三次指数平滑模型参数a, b, c， list
    '''
    s_single = compute_single(alpha, s)
    s_double = compute_single(alpha, s_single)
    s_triple = exponential_smoothing(alpha, s_double)

    a_triple = [0 for i in range(len(s))]
    b_triple = [0 for i in range(len(s))]
    c_triple = [0 for i in range(len(s))]

    for i in range(len(s)):
        a_triple[i] = 3 * s_single[i] - 3 * s_double[i] + s_triple[i]
        b_triple[i] = (alpha / (2 * ((1 - alpha) ** 2))) * ((6 - 5 * alpha) * s_single[i] - 2 * ((5 - 4 * alpha) * s_double[i]) + (4 - 3 * alpha) * s_triple[i])
        c_triple[i] = ((alpha ** 2) / (2 * ((1 - alpha) ** 2))) * (s_single[i] - 2 * s_double[i] + s_triple[i])

    return a_triple, b_triple, c_triple

if __name__ == "__main__":

    '''设置平滑系数值
        1、当时间序列呈现较稳定的水平趋势时，应选较小的α，一般可在0.05~0.20之间取值‘
        2、当时间序列有波动，但长期趋势变化不大时，可选稍大的α值，常在0.1~0.4之间取值；
        3、当时间序列波动很大，长期趋势变化幅度较大，呈现明显且迅速的上升或下降趋势时，宜选择较大的α值，
            如可在0.6~0.8间选值。以使预测模型灵敏度高些，能迅速跟上数据的变化。
        4、当时间序列数据是上升（或下降）的发展趋势类型，α应取较大的值，在0.6~1之间。
    '''
    alpha = 0.12
    data = get_list()
    print(data)
    result=data
    #获取十天的预测销量
    for T in range(10):
        # single=compute_single(alpha,data)
        print("-----------", T, "---------------")
        # print(alpha * data[-1] + (1 - alpha) * single[-1])
        # print("------------------------------")
        # (first,second)=compute_double(alpha,data)
        # print(first[-1]+second[-1]*T)
        # print("-----------------------------")
        (three_first,three_second,three_thired)=compute_triple(alpha,data)
        temp=three_first[-1]+three_second[-1]*T+three_thired[-1]*T*T
        result.append(temp)
        print(three_first[-1]+three_second[-1]*T+three_thired[-1]*T*T)
    plt.plot(data)
    plt.plot(result)
    plt.ylabel("num")
    plt.xlabel("date")
    plt.show()

