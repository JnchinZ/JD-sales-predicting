import requests
import re
import pymysql
import sys

# 进度条
def view_bar(num, total):
    rate = num / total  # 得到现在的比率，0<rate<1
    rate_num = int(rate * 100)  # 将比率百分化，0<rate_num<100
    r = '\r数据爬取进度：[%s%s]' % ("#" * num, " " * (100 - num))  # 进度条封装
    sys.stdout.write(r)  # 显示进度条
    sys.stdout.write(str(rate_num) + '%')  # 显示进度百分比
    sys.stdout.flush()  # 使输出变得平滑

# 使列表变得完美
def perfect_list(*alist):
    blist = []
    for a in alist:
        if len(a) == []:
            a = ['' for i in range(10)]
            blist.append(a)
        elif len(a) != 10:
            if re.search(r'([0-9]{3}[1-9]|[0-9]{2}[1-9][0-9]{1}|[0-9]{1}[1-9][0-9]{2}|[1-9][0-9]{3})-(((0[13578]|1[02])-(0[1-9]|[12][0-9]|3[01]))|((0[469]|11)-(0[1-9]|[12][0-9]|30))|(02-(0[1-9]|[1][0-9]|2[0-8])))', a[0])!=None:
                a[1:] = ['' for i in range(9)]
                blist.append(a)
            else:
                a = ['' for i in range(10)]
                blist.append(a)
        else:
            blist.append(a)
    return blist

# 抓取一个商品的所有评论
class CommentSpider:
    def __init__(self, product_id, score = 0, sort_type = 5):
        self.product_id = product_id  # 商品id
        self.score = score  # 0是全部评论，1是差评，2是中评，3是好评
        self.sort_type = sort_type  # 5是推荐排序，6是时间排序

        # self.page = 0  # 评论页码
        # self.page_size = 10  # 每页评论条数
        pass

    # 组合商品评论的js的url
    def __combineUrl(self, page):
        comments_url = 'https://sclub.jd.com/comment/productPageComments.action?productId=' + \
                       str(self.product_id) + '&score=' + str(self.score) + '&sortType=' + \
                       str(self.sort_type) + '&page=' + str(page) + '&pageSize=10'
        return comments_url


    # 获取页面源代码
    def __visitUrl(self, url):
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.98 Safari/537.36'}
        res = requests.get(url, headers=headers)
        page_content = res.text
        return page_content


    # user_level = re.findall(r'"userImgFlag".*?,"userLevelName":(.*?),', page_content) #用户等级
    # recommend = re.findall(r'"productSales".*?,"recommend":(.*?),', page_content) #追评，暂不研究
    # nickname = re.findall(r'"userLevelId".*?,"isReplyGrade".*?,"nickname":(.*?),', page_content) #用户昵称
    # user_province = re.findall(r'"userImageUrl".*?,"userLevelId".*?,"userProvince":(.*?),"viewCount"', page_content)
    # useful_vote_count = re.findall(r'"referenceType".*?,"Product".*?,"usefulVoteCount":(.*?),"uselessVoteCount"', page_content)

    # 解析网页源代码，获取有用信息
    def __getComments(self, page_content):
        user_client = re.findall(r',"productSales".*?,"userClientShow":"(.*?)",', page_content)  # 用户发布评论时使用的设备类型
        product_color = re.findall(r'userClient".*?,"productColor":"(.*?)",', page_content)  # 用户买的颜色
        product_size = re.findall(r'userClient".*?,"productColor".*?,"productSize":"(.*?)",', page_content)  # 用户买的尺寸

        user_comments = re.findall(r'"id".*?,"topped".*?,"guid".*?,"content":"(.*?)",', page_content)  # 用户评论内容
        comment_date = re.findall(r'"id".*?,"topped".*?,"guid".*?,"content".*?,"creationTime":"(.*?)",',
                                  page_content)  # 评论时间
        score = re.findall(r'"referenceTime".*?,"score":(.*?),', page_content)  # 评分星级
        return user_client, product_color, product_size, user_comments, comment_date, score

        # 获取商品名
    def __get_goods_name(self, page_content):
        goods_name = re.findall(r'"referenceName":"(.*?)",', page_content)  # 商品名
        return goods_name


    # 开始抓取
    def start(self):
        try:
            # 打开数据库连接
            db = pymysql.connect(host='localhost', port=3306, user='root', passwd='1', db='jd_comments', charset="utf8")
            # 使用cursor()方法获取操作游标
            cursor = db.cursor()
        except:
            print('\n数据库连接失败，请检查！！！！！！')
            return

        # 使用 execute() 方法执行 SQL，如果表存在则删除
        cursor.execute("DROP TABLE IF EXISTS item" + str(self.product_id))

        # 使用预处理语句创建表
        create_table_sql = \
            "CREATE TABLE item"+str(self.product_id)+"(\
            comment_date datetime(6) PRIMARY KEY,\
            comment_score INT(1),\
            product_color VARCHAR(255),\
            product_size VARCHAR(255),\
            user_client VARCHAR(255),\
            comment_content text\
            )CHARACTER SET utf8 COLLATE utf8_general_ci;"

        cursor.execute(create_table_sql)

        count_num = 0
        page_num = 0
        while(page_num < 100):
            comments_url = self.__combineUrl(page_num)
            try:
                page_content = self.__visitUrl(comments_url)
            except:
                print('\n访问第'+str(page_num)+'页评论url时失败，已跳过。。。')
                continue
            else:
                if count_num == 0:
                    goods_name = self.__get_goods_name(page_content)
                    count_num += 1

            user_client, product_color, product_size, user_comments, comment_date, score = \
                self.__getComments(page_content)
            user_client, product_color, product_size, user_comments, comment_date, score = \
                perfect_list(user_client, product_color, product_size, user_comments, comment_date, score)
            if comment_date != []:
                for i in range(10):
                    # SQL 插入语句
                    sql = "INSERT INTO item"+str(self.product_id)+ \
                          "(comment_date, comment_score, product_color, product_size, user_client, comment_content) \
                           VALUES ('%s', '%s', '%s', '%s', '%s', '%s')" % \
                           (comment_date[i], score[i], product_color[i], product_size[i], user_client[i], user_comments[i])
                    try:
                        # 执行sql语句
                        cursor.execute(sql)
                        # 提交到数据库执行
                        db.commit()
                    except:
                        # 如果发生错误则回滚
                        db.rollback()
                        print('\n插入失败！>>>'+str(comment_date[i])+','+str(score[i])+','+str(product_color[i])+','+str(product_size[i])+','+str(user_client[i])+','+str(user_comments[i]))
                pass
            else:
                print('\n第',page_num,'页评论为空，停止爬虫')
                break
            page_num += 1
            view_bar(page_num, 100)

        # # 将商品名存入数据库
        # print("INSERT INTO goods_info(goods_id, goods_name) \
        #                 VALUES ('%s', '%s')" % (self.product_id, goods_name))
        # cursor.execute("INSERT INTO goods_info(goods_id, goods_name) \
        #         VALUES ('%s', '%s')" %(self.product_id, goods_name))
        # print("INSERT INTO goods_info(goods_id, goods_name) \
        #         VALUES ('%s', '%s')" %(self.product_id, goods_name))

        # 关闭数据库连接
        db.close()
        print('\n本商品评论抓取结束，一共',page_num,'页评论')
    # # 获取最大评论页数
    # def getMaxPage(self):
    #     max_page = re.findall(r',"maxPage":(.*?),', page_content)[0]  # 用户发布评论时使用的设备类型
    #     return int(max_page)

if __name__ == '__main__':
    product_id_list = [675971,4209217]
    for product_id in product_id_list:
        comment_spider = CommentSpider(product_id)
        comment_spider.start()

