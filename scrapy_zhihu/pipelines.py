# -*- coding: utf-8 -*-
from os.path import exists ,join,getsize
from os import mkdir
from .items import UserItem, AnswerItem,FolloweeItem,FollowerItem,AnswerCommentItem,QuestionItem,QuestionAnswerItem
from json import dump,load
from pymongo import MongoClient
from .spiders.zhihu import user_name
from datetime import datetime
class MyPipeline(object):
    def __init__(self, download_path: str,
                 use_db: bool,
                 mongodb_uri: str,
                 db_name: str,
                 user: str,
                 pwd: str):
        self.__download_path = download_path
        self.__use_db = use_db
        self.__db_uri = mongodb_uri
        self.__db_name = db_name
        self.__client = MongoClient(self.__db_uri)
        self.__db = self.__client[self.__db_name]
        self.__user = user
        self.__pwd = pwd

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            download_path=crawler.settings.get('DOWNLOAD_PATH'),
            use_db=crawler.settings.get('USE_DB'),
            mongodb_uri=crawler.settings.get('MONGO_URI'),
            db_name=crawler.settings.get('DB_NAME'),
            user=crawler.settings.get("USER_NAME"),
            pwd=crawler.settings.get("PASSWORD"),
        )

    def close_spider(self, spider):
        self.__client.close()

    def process_item(self, item, spider):
        # 可以选择存储到数据库
        if self.__use_db:
            self.__db['user'].update({'url_token': item["url_token"]}, {'$set': item}, True)
        # 也可以存储到本地data目录下txt文档
        else:
            # 用户个人信息
            def get_current_time():
                return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            if isinstance(item, UserItem):
                file_name = self.__download_path + item['name'] + '.json'  # 文件扩展名为 .json
                with open(file_name, 'w', encoding='utf-8') as f:  # 使用 'w' 模式，覆盖文件
                    dump(dict(item), f,
                        ensure_ascii=False,
                        separators=(',', ': '),
                        indent=4)
                print(f"[{get_current_time()}] 用户【{item['name']}】的数据爬取完毕")

            # 用户回答信息
            elif isinstance(item, AnswerItem):
                answer_folder = self.__download_path + user_name + '_answers/'
                if not exists(answer_folder):
                    mkdir(answer_folder)
                file_name = answer_folder + str(item['answer_num']) + '.json'
                with open(file_name, 'w', encoding='utf-8') as f:
                    dump(dict(item), f,
                        ensure_ascii=False,
                        separators=(',', ': '),
                        indent=4)
                print(f"[{get_current_time()}] 用户【{user_name}】的回答【{item['answer_num']}】数据保存完毕")

            elif isinstance(item, AnswerCommentItem):
                answer_folder = self.__download_path + user_name + '_answers/'
                file_name = answer_folder + str(item['answer_num']) + '.json'
                with open(file_name, 'a', encoding='utf-8') as f:
                    dump(dict(item), f,
                        ensure_ascii=False,
                        separators=(',', ': '),
                        indent=4)
                print(f"[{get_current_time()}] 用户【{user_name}】的回答【{item['answer_num']}】数据保存完毕")
                print(f"[{get_current_time()}] 用户【{user_name}】的回答【{item['answer_num']}】的评论【{item['comment_author']}】数据保存完毕")

            elif isinstance(item, QuestionItem):
                question_folder = self.__download_path + user_name + '_questions/'
                if not exists(question_folder):
                    mkdir(question_folder)
                file_name = question_folder + str(item['question_num']) + '.json'
                with open(file_name, 'w', encoding='utf-8') as f:
                    dump(dict(item), f,
                        ensure_ascii=False,
                        separators=(',', ': '),
                        indent=4)
                print(f"[{get_current_time()}] 用户【{user_name}】的提问【{item['question_num']}】的回答【{item['answer_num']}】数据保存完毕")

                

            elif isinstance(item, FolloweeItem):
                file_name = self.__download_path + user_name + "_followees.json"
    
                # 初始化数据
                data = []
                
                # 如果文件存在且不为空，尝试读取
                if exists(file_name) and getsize(file_name) > 0:
                    try:
                        with open(file_name, 'r', encoding='utf-8') as f:
                            data = load(f)
                    except ValueError:
                        data = []  # 文件内容无效时初始化为空列表
                
                # 添加新数据
                data.append(dict(item))
                # 限制最多保存10条数据
                if len(data) > 10:
                    data = data[-10:]  # 只保留最新的10条数据
                # 写入完整数据
                with open(file_name, 'w', encoding='utf-8') as f:
                    dump(data, f, ensure_ascii=False, indent=4)
                
                print(f"[{get_current_time()}] 用户【{user_name}】的关注者【{item['name']}】数据保存完毕")

            elif isinstance(item, FollowerItem):  # 假设你有一个 FollowersItem
                file_name = join(self.__download_path, f"{user_name}_followers.json")
    
                # 初始化数据
                data = []
                
                # 如果文件存在且不为空，尝试读取
                if exists(file_name) and getsize(file_name) > 0:
                    try:
                        with open(file_name, 'r', encoding='utf-8') as f:
                            data = load(f)
                    except ValueError:
                        data = []  # 文件内容无效时初始化为空列表
                
                # 添加新数据
                data.append(dict(item))
                # 限制最多保存10条数据
                if len(data) > 10:
                    data = data[-10:]  # 只保留最新的10条数据
                # 写入完整数据
                with open(file_name, 'w', encoding='utf-8') as f:
                    dump(data, f, ensure_ascii=False, indent=4)
                print(f"[{get_current_time()}] 用户【{user_name}】的粉丝【{item['name']}】数据保存完毕")

            return item
        return item