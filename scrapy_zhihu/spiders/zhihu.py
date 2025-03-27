from json import load,dump,loads,dumps
from scrapy import Spider, Request
from scrapy_zhihu.items import UserItem, AnswerItem, FolloweeItem,FollowerItem,AnswerCommentItem, QuestionItem,QuestionAnswerItem
from scrapy_zhihu.cookie import load_cookies
from urllib.parse import urljoin
from os.path import exists
from os import remove
from scrapy_zhihu.settings import *
from DrissionPage import ChromiumPage,ChromiumOptions
from DrissionPage.common import By
from bs4 import BeautifulSoup
from datetime import datetime
import shutil
from time import sleep,time
import logging
import shutil

logging.basicConfig(
    level=logging.INFO,  # 日志级别
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # 日志格式
    filename='zhihu_spider.log',  # 日志文件
    filemode='a'  # 追加模式
)
logger = logging.getLogger(__name__)  # 创建日志记录器
class ZhihuSpider(Spider):
    def parse(self, response):
        
        pass
    name = "zhihu"
    user_token = None
    url_token_cookies = None
    allowed_domains = ["www.zhihu.com"]
    start_urls = ['http://www.zhihu.com/']

    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)
        # 从命令行参数中获取用户名称和功能选项
        self.user_name = kwargs.get('user_name', '廖雪峰')
        self.func = kwargs.get('func', '1')  # 默认功能是查询用户信息
        global user_name 
        user_name = self.user_name

    # 起始用户
    def clean_headers(self, headers):
        cleaned_headers = {}
        for key, value in headers.items():
            if not key.startswith(':'):  # 移除以冒号开头的 HTTP/2 头字段
                cleaned_headers[key] = value
        return cleaned_headers

    
    def search_username_get_href(self):    
        try:
            # 创建浏览器对象（正确参数传递方式）
            co = ChromiumOptions()
            page = ChromiumPage(co)
            
            # 设置cookies
            cookies = load_cookies()   # 确保这个函数返回正确的cookies格式
            if cookies:
                page.set.cookies(cookies)
        except Exception as e:
            print(f"浏览器初始化失败: {e}")
            return None
        
        # 打开知乎并搜索
        page.get('https://www.zhihu.com')
        page.set.scroll.smooth(on_off=True)  # 启用平滑滚动
        
        page.ele('#Popover1-toggle').clear().input(self.user_name)
        page.ele('@aria-label=搜索', timeout=10).click()
        #page.ele(".SearchTabs-customFilterEntry").click()

        # 点击用户
        loc1 = (By.XPATH, '//*[@id="root"]/div/main/div/div[1]/div[1]/div/ul/span[2]/li/a')
        page.ele(loc1).click()
        
        # 获取用户链接
        href = (By.XPATH, '//*[@id="SearchMain"]/div/div/div/div[2]/div/div/div/div/div/div[2]/h2/span/div/span/div/a')
        href_html = page.ele(href).html
        soup = BeautifulSoup(href_html, 'html.parser')
        href = soup.a['href'][2:]
        href = 'https://' + href
        tab = page.latest_tab
        tab.listen.start('sidebar?q=')
        while 1:
            tab.refresh()
            res = tab.listen.wait()
            if "cookie" in res.request.headers:
                self.user_headers = self.clean_headers(res.request.headers)
                break
        self.user_token = href.split('/')[-1]
        print(href)

        # 点击粉丝，获取粉丝 API 的 headers
        page.set.window.full()
        follower = (By.XPATH, f'//*[@id="SearchMain"]/div/div/div/div[2]/div/div/div/div/div/div[2]/div/div/div[2]/a[3]')
        page.ele(follower).click()
        tab = page.latest_tab
        tab.listen.start('/followers?include=')
        while 1:
            tab.refresh()
            res = tab.listen.wait()
            if "cookie" in res.request.headers:
                self.followers_headers = self.clean_headers(res.request.headers)
                break

        # 重新刷新页面，获取回答 API 的 headers
        tab.refresh()
        answer = (By.XPATH, f'//*[@id="ProfileMain"]/div[1]/ul/li[2]/a')
        tab.ele(answer).click()
        tab = page.latest_tab
        tab.listen.start('/answers?include=')
        while 1:
            tab.refresh()
            res = tab.listen.wait()
            if "Cookie" in res.request.headers:
                self.answer_headers = self.clean_headers(res.request.headers)
                break

        # 获取回答评论的 headers
        answer_comment_num = 1
        self.answer_comments_headers = {}
        tab = page.latest_tab
        while answer_comment_num <= 10:
            tab.listen.start('root_comment?order_by=score&limit=20&offset=')
            answer_comment = (By.XPATH, f'//*[@id="Profile-answers"]/div[2]/div[{answer_comment_num+1}]/div/div/div[2]/div/button[1]')
            tab.ele(answer_comment).click()
            res = tab.listen.wait()
            self.answer_comments_headers[answer_comment_num] = self.clean_headers(res.request.headers)
            answer_comment_num += 1

        # 获取提问 API 的 headers
        question = (By.XPATH, f'//*[@id="ProfileMain"]/div[1]/ul/li[4]/a')
        tab.ele(question).click()
        tab = page.latest_tab
        tab.listen.start('/questions?include=')
        while 1:
            tab.refresh()
            res = tab.listen.wait()
            if "Cookie" in res.request.headers:
                self.question_headers = self.clean_headers(res.request.headers)
                break

        # 将所有 headers 存储为一个字典
        headers_data = {
            "user_token" : self.user_token,
            "user_headers": self.user_headers,
            "followers_headers": self.followers_headers,
            "answer_headers": self.answer_headers,
            "answer_comments_headers": self.answer_comments_headers,
            "question_headers": self.question_headers
        }

        # 保存到 JSON 文件
        headers_file = f"D:\\scrapy_zhihu\\data\\{self.user_name}_headers.json"
        self.save_headers_to_json(headers_data, headers_file)

        page.quit()
    def get_question_answer(self,question_num):
        try:
            # 创建浏览器对象（正确参数传递方式）
            co = ChromiumOptions()
            page = ChromiumPage(co)
            
            # 设置cookies
            cookies = load_cookies()   # 确保这个函数返回正确的cookies格式
            if cookies:
                page.set.cookies(cookies)
        except Exception as e:
            print(f"浏览器初始化失败: {e}")
            return None
        page.set.cookies(load_cookies())
        filename = DOWNLOAD_PATH+self.user_name + '_questions/' + str(question_num) + '.json'
        with open(filename, 'r',encoding= 'utf-8') as f:
            question = loads(f.read())
        question_url = question['question_url']    
        page.get(question_url)
        page.set.window.full()
        
        # 获取问题详细内容
        try:
            page.ele('css:button.Button.QuestionRichText-more.FEfUrdfMIKpQDJDqkjte.Button--plain.fEPKGkUK5jyc4fUuT0QP',timeout=1).click() #点击展开全文
            sleep(0.5) 
            question_content = page.ele((By.CLASS_NAME, 'RichText ztext css-ob6uua')).text
            question_link = page.ele((By.CLASS_NAME, 'RichText ztext css-ob6uua')).link
            question_detail = {'question_detail':question_content,'question_photo':question_link}
            with open(filename, 'w', encoding='utf-8') as f:
                question['question_detail'] = question_detail
                f.write(dumps(question, ensure_ascii=False, indent=4))
            print(f"问题 {question_num} 的详情已成功写入文件。")
        except:
            pass
        page.set.scroll.smooth(on_off=False)    # 关闭平滑滚动
        # 设置滚动时间限制
        start_time = time()  # 记录开始时间
        scroll_time_limit = 10  # 滚动时间限制为 10 秒

        # 开始滚动
        while True:
            if time() - start_time >= scroll_time_limit:
                print("滚动时间达到 5 秒，停止滚动。")
                break

            page.scroll.down(3000)  # 每次滚动 500 像素，可根据需要调整
            sleep(0.2)  # 等待滚动完成
        # 获取具有十个回答的页面HTML
        html = page.html
        # 解析HTML
        page.quit()
        return html 
                
   
    def save_headers_to_json(self, headers_data, filename):
        """
        将 headers 保存到 JSON 文件
        """
        with open(filename, 'w', encoding='utf-8') as f:
            dump(headers_data, f, ensure_ascii=False, indent=4)
        print(f"Headers saved to {filename}")

    def load_headers_from_json(self, filename):
        """
        从 JSON 文件加载 headers
        """
        if exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                headers_data = load(f)
            print(f"Headers loaded from {filename}")
            return headers_data
        else:
            print(f"Headers file {filename} does not exist")
            return None
    
   
    # 用户信息url
    user_url = "https://www.zhihu.com/people/{user_token}"
    #print(user)
    
    # 关注列表的url
    follows_url = "https://www.zhihu.com/api/v4/members/{user_token}/followees?include={include}&offset={offset}&limit={limit}"
    # 关注列表的查询参数
    followees_query = "data%5B*%5D.answer_count%2Carticles_count%2Cgender%2Cfollower_count%2Cis_followed%2Cis_following%2Cbadge%5B%3F%28type%3Dbest_answerer%29%5D.topics"

    # 获取粉丝列表信息的url
    followers_url = "https://www.zhihu.com/api/v4/members/{user_token}/followers?include={include}&offset={offset}&limit={limit}"

    # 粉丝列表的查询参数
    followers_query = "data%5B*%5D.answer_count%2Carticles_count%2Cgender%2Cfollower_count%2Cis_followed%2Cis_following%2Cbadge%5B%3F%28type%3Dbest_answerer%29%5D.topics"

    # 回答按时间的查询url
    answers_url = 'https://www.zhihu.com/api/v4/members/{user_token}/answers?include={include}&offset={offset}&limit={limit}&sort_by=created&ws_qiangzhisafe=0'

    # 回答前10的查询参数
    answer_query = 'data%5B*%5D.is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cattachment%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_info%2Cexcerpt%2Cpaid_info%2Creaction_instruction%2Cis_labeled%2Clabel_info%2Crelationship.is_authorized%2Cvoting%2Cis_author%2Cis_thanked%2Cis_nothelp%3Bdata%5B*%5D.vessay_info%3Bdata%5B*%5D.author.badge%5B%3F%28type%3Dbest_answerer%29%5D.topics%3Bdata%5B*%5D.author.kvip_info%3Bdata%5B*%5D.author.vip_info%3Bdata%5B*%5D.question.has_publishing_draft%2Crelationship'
    
    answers_comment_url = 'https://www.zhihu.com/api/v4/comment_v5/answers/{answer_id}/root_comment?order_by=score&limit=20&offset='
    
    questions_url = 'https://www.zhihu.com/api/v4/members/{user_token}/questions?include={include}&offset={offset}&limit={limit}&ws_qiangzhisafe=0'

    question_query = 'data%5B*%5D.created%2Canswer_count%2Cfollower_count%2Cauthor%2Cadmin_closed_comment'
    
    question_answers_url = 'https://www.zhihu.com/question/{question_id}'
    question_answers_query = 'data%5B*%5D.created%2Canswer_count%2Cfollower_count%2Cauthor%2Cadmin_closed_comment%2Cvoteup_count%2Ccomment_count%2Ccontent%2Cexcerpt%2Cquestion%2Cquestion.detail%2Cquestion.id%2Cquestion.title%2Cquestion.url%2Cquestion.topics%2Cquestion.topics%5B*%5D.id%'
    #行为url
    activate_url ='https://www.zhihu.com/api/v3/moments/{user_token}/activities?limit=5&desktop=true&ws_qiangzhisafe=0'
    def start_requests(self):
        """
        重写start_requests方法，请求了用户查询、关注列表、粉丝列表（前20人）
        :return: 请求
        """
        headers_file = f"D:\\scrapy_zhihu\\data\\{self.user_name}_headers.json"
        headers_data = self.load_headers_from_json(headers_file)

        if not headers_data:
            # 如果 JSON 文件不存在，调用 search_username_get_href 获取 headers
            self.search_username_get_href()
            headers_data = {
                "user_token" : self.user_token, # 用户 token
                "user_headers": self.user_headers, # 用户 headers
                "followers_headers": self.followers_headers,
                "answer_headers": self.answer_headers,
                "answer_comments_headers": self.answer_comments_headers,
                "question_headers": self.question_headers
            }
        
        func_list = self.func.split()
        for func in func_list:
        
            if func == '1':
                self.user_token = headers_data.get("user_token")
                yield Request(
                    self.user_url.format(user_token=self.user_token),
                    headers= headers_data.get("user_headers"),
                    callback=self.parse_user
                )
            
            elif func == '2':
            #删除已有关注者文件，重新爬取
                file_name = DOWNLOAD_PATH+self.user_name+"_followees"+'.json'
                if  exists (file_name):
                    remove(file_name)
                yield Request(
                    self.follows_url.format(user_token=headers_data.get("user_token"), include=self.followees_query, offset=0, limit=10),
                    headers =  headers_data.get("user_headers"),
                    callback=self.parse_followees 
                )
                self.followees = 0   
            
            elif func == '3':
                #删除已有粉丝文件，重新爬取
                file_name = DOWNLOAD_PATH+self.user_name+"_followers"+'.json'
                if  exists (file_name):
                    remove(file_name)
                #因为知乎反爬，而加密参数破解困难，所以直接抓取浏览器自身调用API接口的发送包，进行header头替换，再发送请求，目前只能一次性抓取20个
                yield Request(
                    self.followers_url.format(user_token=headers_data.get("user_token"), include=self.followers_query, offset=0, limit=20),
                    headers=headers_data.get("followers_headers"),
                    callback=self.parse_followers,
                )
                self.followers = 0
            
            elif func == '4':
                #删除已有回答文件夹，重新爬取
                file_name = DOWNLOAD_PATH+ self.user_name + '_answers/'
                if  exists (file_name):
                    shutil.rmtree(file_name) #删除已有回答文件夹，重新爬取
                #因为知乎反爬，而加密参数破解困难，所以直接抓取浏览器自身调用API接口的发送包，进行header头替换，再发送请求，目前只能一次性抓取20个
                yield Request(
                    self.answers_url.format(user_token=headers_data.get("user_token"), include=self.answer_query, offset=0, limit=20),
                    callback=self.parse_answers,
                    headers=headers_data.get("answer_headers")
                )
                self.answers = 0
            elif func == '5':
                #删除已有问题文件夹，重新爬取
                file_name = DOWNLOAD_PATH+ self.user_name + '_questions/'
                if  exists (file_name):
                    shutil.rmtree(file_name) #删除已有回答文件夹，重新爬取
                #因为知乎反爬，而加密参数破解困难，所以直接抓取浏览器自身调用API接口的发送包，进行header头替换，再发送请求，目前只能一次性抓取20个
                yield Request(
                    self.questions_url.format(user_token=headers_data.get("user_token"), include=self.question_query, offset=0, limit=20),
                    callback=self.parse_questions,
                    headers=headers_data.get("question_headers")
                )
                self.questions= 0
            elif func == '6':
            # 功能 6：更新 headers 并重新爬取所有数据
            # 重新调用 search_username_get_href 更新 headers
                self.search_username_get_href()
                headers_data = {
                    "user_token": self.user_token,  # 用户 token
                    "user_headers": self.user_headers,  # 用户 headers
                    "followers_headers": self.followers_headers,
                    "answer_headers": self.answer_headers,
                    "answer_comments_headers": self.answer_comments_headers,
                    "question_headers": self.question_headers
                }

                # 执行功能 1-5
                yield Request(
                    self.user_url.format(user_token=headers_data.get("user_token")),
                    headers=self.user_headers,
                    callback=self.parse_user
                )

                # 功能 2：更新关注列表
                file_name = DOWNLOAD_PATH + self.user_name + "_followees" + '.json'
                if exists(file_name):
                    remove(file_name)
                yield Request(
                    self.follows_url.format(user_token=headers_data.get("user_token"), include=self.followees_query, offset=0, limit=10),
                    headers =  headers_data.get("user_headers"),
                    callback=self.parse_followees   
                )
                self.followees = 0

                # 功能 3：更新粉丝列表
                file_name = DOWNLOAD_PATH + self.user_name + "_followers" + '.json'
                if exists(file_name):
                    remove(file_name)
                yield Request(
                    self.followers_url.format(user_token=headers_data.get("user_token"), include=self.followers_query, offset=0, limit=20),
                    headers=headers_data.get("followers_headers"),
                    callback=self.parse_followers,
                )
                self.followers = 0

                # 功能 4：更新回答列表
                file_name = DOWNLOAD_PATH + self.user_name + '_answers/'
                if exists(file_name):
                    shutil.rmtree(file_name)
                yield Request(
                    self.answers_url.format(user_token=headers_data.get("user_token"), include=self.answer_query, offset=0, limit=20),
                    callback=self.parse_answers,
                    headers=headers_data.get("answer_headers")
                )
                self.answers = 0

                # 功能 5：更新问题列表
                file_name = DOWNLOAD_PATH + self.user_name + '_questions/'
                if exists(file_name):
                    shutil.rmtree(file_name)
                yield Request(
                    self.questions_url.format(user_token=headers_data.get("user_token"), include=self.question_query, offset=0, limit=20),
                    callback=self.parse_questions,
                    headers=headers_data.get("question_headers")
                )
                self.questions = 0
            elif func == '7':
                    print("已开启自动更新回答和提问")
                    try:
                        # 初始化浏览器页面
                        page = ChromiumPage()
                        page.set.cookies(load_cookies())
                        page.get('https://www.zhihu.com')
                        page.set.scroll.smooth(on_off=True)  # 启用平滑滚动
                        page.ele("#Popover1-toggle").clear().input(self.user_name)
                        page.ele(".Button SearchBar-searchButton FEfUrdfMIKpQDJDqkjte Button--primary Button--blue epMJl0lFQuYbC7jrwr_o JmYzaky7MEPMFcJDLNMG").click()
                        page.ele(".SearchTabs-customFilterEntry").click()

                        # 点击用户
                        loc1 = (By.XPATH, '//*[@id="root"]/div/main/div/div[1]/div[1]/div/ul/span[2]/li/a')
                        page.ele(loc1).click()

                        # 获取用户 token
                        href = (By.XPATH, '//*[@id="SearchMain"]/div/div/div/div[2]/div/div/div/div/div/div[2]/h2/span/div/span/div/a')
                        href_html = page.ele(href).html
                        soup = BeautifulSoup(href_html, 'html.parser')
                        href = soup.a['href'][2:]
                        href = 'https://' + href
                        self.user_token = href.split('/')[-1]
                        page.set.window.full()
                        loc2 = (By.XPATH, '//*[@id="SearchMain"]/div/div/div/div[2]/div/div/div/div/div/div[2]/h2/span/div/span[1]/div/a')
                        page.ele(loc2).click()
                        # 监听活动请求
                        tab = page.latest_tab
                        tab.listen.start('/activities?limit')
                        while 1:    
                            tab.refresh()
                            res = tab.listen.wait()  # 设置超时时间
                            if "Cookie" in res.request.headers:
                                self.activate_headers = self.clean_headers(res.request.headers)
                                    
                                yield Request(
                                        self.activate_url.format(user_token=self.user_token),
                                        headers=self.activate_headers,
                                        callback=self.parse_activate
                                        )
                                page.quit()
                                break
                    except Exception as e:
                        print(f"更新回答和提问数据时发生错误: {e}")
                     


        
    def parse_user(self, response):
        """
        因为返回的是html格式的数据
        :param response: 网页响应数据
        :return: item，并返回该用户的的信息     
        """
        #先将html格式的数据转换为json格式
    
        user_text = response.text
        json_text = BeautifulSoup(user_text, "html.parser").find("script", attrs={"id": "js-initialData"}).text
        result = loads(json_text)["initialState"]["entities"]["users"][self.user_token]
        #根据item的字段提取用户信息，如果没有则返回"未知"
        #用户名、性别、IP地址、居住地、一句话介绍、所在行业、职业经历、个人简介
        gender_map = {1: "男", 2: "女"}
        item = UserItem(  
        name = result.get("name", "未知"),
        url_token = self.user_token,
        gender = gender_map.get(result.get("gender"), "未知"),
        locations = result.get("locations", [{}])[0].get("name", "未知") if result.get("locations") else "未知",
        IP_address = result.get("ipInfo", "未知")[5:] if result.get("ipInfo") else "未知",
        headline = result.get("headline", "未知"),
        description = result.get("description", "未知"),
        business = result.get("business", {}).get("name", "未知"),
        employments = [employment.get("company", {}).get("name", "未知") for employment in result.get("employments", [])] or ["未知"],
        educations = [education.get("school", {}).get("name", "未知") for education in result.get("educations", [])] or ["未知"]
        )
        # 返回用户信息
        yield item
        print(f"用户【{self.user_name}】的信息保存完毕")
       
    def parse_answers(self, response):
        """
        用户回答列表的解析
        :param response: 网页响应数据
        :return: 网页请求
        """
        headers_file = f"D:\\scrapy_zhihu\\data\\{self.user_name}_headers.json"
        headers_data = self.load_headers_from_json(headers_file)

        results = loads(response.text)
        if 'data' in results.keys():
            for result in results.get('data',[]):
                self.answers += 1
                if self.answers >= 11:
                    self.answers -= 1 
                    break
                answer_item = AnswerItem(
                answer_num = self.answers,
                answer_id = result.get("id", "未知"),
                answer_time = datetime.fromtimestamp(result.get("updated_time", "未知")).strftime("%Y-%m-%d %H:%M:%S"),
                question = result.get("question", {}).get("title", "未知"),
                content = result.get("content", "未知"),
                voteup_count = result.get("voteup_count", 0),
                comment_count = result.get("comment_count", 0),
                answer_url = result.get("url", "未知"),
                answer_comment=[],  # 初始化评论列表
                )
                #请求每条回答下面的评论
                if answer_item['comment_count'] > 0:
                    yield Request(
                        self.answers_comment_url.format(answer_id = answer_item['answer_id']),
                        callback=self.parse_answer_comments,
                        headers = headers_data.get("answer_comments_headers").get(str(self.answers)),
                        meta={'answer_item': answer_item}, # 传递当前回答
                        )
                else :
                    yield answer_item  
                    
        print(f"用户【{self.user_name}】的回答共{self.answers}条数据保存完毕")
    def parse_answer_comments(self, response):
        answer_item = response.meta['answer_item']  # 从 meta 中获取回答序号
        results = loads(response.text)
        self.answer_comments = 0
        if 'data' in results.keys():
            for result in results.get('data',[]):
                self.answer_comments += 1
                if self.answer_comments >= 11:
                    self.answer_comments -= 1 
                    break
                comment_item = AnswerCommentItem(
                comment_num =self.answer_comments,    # 回答序号
                comment_id = result.get("author", {}).get("id", "未知"),
                comment_author = result.get("author", {}).get("name", "未知"),
                comment_time = datetime.fromtimestamp(result.get("created_time", "未知")).strftime("%Y-%m-%d %H:%M:%S"),
                comment_content = result.get("content", "未知"),
                )
                answer_item['answer_comment'].append(dict(comment_item))
            yield answer_item
        print(f"用户【{self.user_name}】的回答【{answer_item['answer_num']}】的评论共{self.answer_comments}条数据保存完毕")  
    def parse_questions(self, response):
        """
        用户提问列表解析
        :param response: 网页响应数据
        :return: json格式包含data和page的数据
        """ 
        results = loads(response.text)
        if 'data' in results.keys():
            for result in results.get('data',[]):
                self.questions += 1
                if self.questions > 10:
                    self.questions -= 1 
                    break
                item = QuestionItem(
                question_num = self.questions,
                question_id = result.get("id", "未知"),
                question_url = urljoin("https://www.zhihu.com/question/", result.get("id", "未知")),
                question = result.get("title", "未知"),
                question_time = datetime.fromtimestamp(result.get("created", "未知")).strftime("%Y-%m-%d %H:%M:%S"),
                answer_count = result.get("answer_count", 0),
                question_answer = []  # 初始化回答列表
                )
                yield item
                #请求每条问题下面的回答
                if item['answer_count'] > 0:
                    response = self.get_question_answer(self.questions)
                    soup = BeautifulSoup(response, 'html.parser')
                    #获取所有回答的标签
                    answers = soup.find_all('div', class_='List-item')
        
                    answers_num = 0
                    for answer in answers:
                        answers_num += 1
                        if answers_num > 10:
                            break
                        try:
                            # 解析 answer_id
                            extra_module_div = answer.find('div', {'data-za-extra-module': True})
                            if extra_module_div:
                                extra_module = loads(extra_module_div['data-za-extra-module'])
                                answer_id = extra_module['card']['content']['author_member_hash_id']
                            else:
                                answer_id = None

                            # 创建 QuestionAnswerItem
                            question_answer = QuestionAnswerItem(
                                question_num=self.questions,
                                answer_num=answers_num,
                                answer_id=answer_id,
                                answer_author=answer.find('meta', itemprop='name')['content'],
                                answer_time=answer.find('span', {'data-tooltip': True})['data-tooltip'].replace("发布于 ", ""),
                                answer_voteup_count=int(answer.find('meta', itemprop='upvoteCount')['content']),
                                answer_content=answer.find('div', class_='RichContent-inner').get_text().strip()
                            )
                        except (KeyError, TypeError, AttributeError) as e:
                            # 如果解析失败或键不存在，打印错误并跳过当前 answer
                            print(f"Error parsing answer: {e}")
                            continue  # 如果在一个循环中，跳过当前 answer
                
                        images = answer.find('div', class_='RichContent-inner').find_all('img')
                        images_urls = [img['src'] for img in images if 'src' in img.attrs]
                        question_answer['image_urls'] = images_urls
                        item['question_answer'].append(dict(question_answer))
                        yield item
                    print(f"问题 {self.questions} 的回答共{answers_num}条已成功写入文件。")
            print(f"用户【{self.user_name}】的提问共{self.questions}条数据保存完毕")

    def parse_followees(self, response):
        """
        用户关注列表解析
        :param response: 网页响应数据
        :return: json格式包含data和page的数据
        """
        results = loads(response.text)
        if 'data' in results.keys():
            for result in results.get('data',[]):
                self.followees += 1
                if self.followees >= 11:
                    self.followees -= 1 
                    break
                item = FolloweeItem(
                name=result.get("name"),
                url=urljoin("https://www.zhihu.com/people/", result.get("url_token", "")),
                answer_count=result.get("answer_count", 0),  # 确保提取 answer_count
                articles_count=result.get("articles_count", 0),  # 确保提取 articles_count
                follower_count=result.get("follower_count", 0),  # 确保提取 follower_count    
                gender =  result.get("gender", -1), # 1 男 0 女 -1 未知
                headline = result.get("headline", "未知"),
                )
                yield item
        if 'page' in results.keys() and not results.get('is_end'):
            next_page = results.get('paging').get('next')
            yield Request(next_page, callback=self.parse_followees)  # 添加cookies"
        print(f"用户【{self.user_name}】的关注者共{self.followees}人数据保存完毕")
    def parse_followers(self, response):
        """
        用户粉丝列表解析
        :param response: 网页响应数据
        :return: json格式包含data和page的数据
        """
        results = loads(response.text)
        if 'data' in results.keys():
            for result in results.get('data',[]):
                self.followers += 1
                if self.followers >= 11:
                    self.followers -= 1 
                    break
                item = FollowerItem(
                name=result.get("name"),
                url=urljoin("https://www.zhihu.com/people/", result.get("url_token", "")),
                answer_count=result.get("answer_count", 0),  # 确保提取 answer_count
                articles_count=result.get("articles_count", 0),  # 确保提取 articles_count
                follower_count=result.get("follower_count", 0),  # 确保提取 follower_count    
                gender =  result.get("gender", -1), # 1 男 0 女 -1 未知
                headline = result.get("headline", "未知"),
                )
                yield item
        if 'page' in results.keys() and not results.get('is_end'):
            next_page = results.get('paging').get('next')
            yield Request(next_page, callback=self.parse_followers)  
        print(f"用户【{self.user_name}】的粉丝共{self.followers}人数据保存完毕") 
    def parse_activate(self, response):
        print("开始检查用户动态")
        results = loads(response.text)
        if 'data' in results.keys():
            result = results.get('data',[])
            results = result[0]
            if results.get('action_text') == '回答了问题':
                create_time = datetime.fromtimestamp(results.get('created_time', '未知')).strftime('%Y-%m-%d %H:%M:%S')
                file_path = f"D:\\scrapy_zhihu\\{user_name}_answers\\update.json"

                # 检查文件是否存在
                if not exists(file_path):
                    # 如果文件不存在，创建新的文件并保存 create_time
                    data = {'old_answer_time': create_time}
                    with open(file_path, 'w', encoding='utf-8') as file:
                        dump(data, file, ensure_ascii=False, indent=4)
                else:
                    # 如果文件存在，读取文件内容并更新 question_time
                    with open(file_path, 'r', encoding='utf-8') as file:
                        data = load(file)
                        # 提取 answer_time
                        old_answer_time = data.get('old_answer_time', '未知')
                    if create_time != old_answer_time:
                        print(f"用户【{user_name}】的回答有更新")
                        self.search_username_get_href()
                        headers_data = {
                        "user_token": self.user_token,  # 用户 token
                        "user_headers": self.user_headers,  # 用户 headers
                        "followers_headers": self.followers_headers,
                        "answer_headers": self.answer_headers,
                        "answer_comments_headers": self.answer_comments_headers,
                        "question_headers": self.question_headers
                        }
                        file_name = DOWNLOAD_PATH + self.user_name + '_answers/'
                        if exists(file_name):
                            shutil.rmtree(file_name)
                        yield Request(
                            self.answers_url.format(user_token=headers_data.get("user_token"), include=self.answer_query, offset=0, limit=20),
                            callback=self.parse_answers,
                            headers=headers_data.get("answer_headers")
                        )
                        self.answers = 0
                        data['old_answer_time'] = create_time
                                # 将更新后的数据写回文件
                        with open(file_path, 'w', encoding='utf-8') as file:
                            dump(data, file, ensure_ascii=False, indent=4)
                    else:
                        print(f"用户【{user_name}】的回答无更新")
            elif results.get('action_text') == '添加了问题':
                create_time = datetime.fromtimestamp(results.get('created_time', '未知')).strftime('%Y-%m-%d %H:%M:%S')
                file_path = f"D:\\scrapy_zhihu\\data\\{user_name}_questions\\update.json"

                # 检查文件是否存在
                if not exists(file_path):
                    # 如果文件不存在，创建新的文件并保存 create_time
                    data = {'old_question_time': create_time}
                    with open(file_path, 'w', encoding='utf-8') as file:
                        dump(data, file, ensure_ascii=False, indent=4)
                else:
                    # 如果文件存在，读取文件内容并更新 question_time
                    with open(file_path, 'r', encoding='utf-8') as file:
                        data = load(file)
                        # 提取 answer_time
                        old_question_time = data.get('old_question_time', '未知')
                    if create_time != old_question_time:
                        print(f"用户【{user_name}】的提问有更新")
                        self.search_username_get_href()
                        headers_data = {
                        "user_token": self.user_token,  # 用户 token
                        "user_headers": self.user_headers,  # 用户 headers
                        "followers_headers": self.followers_headers,
                        "answer_headers": self.answer_headers,
                        "answer_comments_headers": self.answer_comments_headers,
                        "question_headers": self.question_headers
                        }
                        file_name = DOWNLOAD_PATH + self.user_name + '_questions/'
                        if exists(file_name):
                            shutil.rmtree(file_name)
                        yield Request(
                            self.questions_url.format(user_token=headers_data.get("user_token"), include=self.question_query, offset=0, limit=20),
                            callback=self.parse_questions,
                            headers=headers_data.get("question_headers")
                        )
                        self.questions = 0
                        data['old_question_time'] = create_time
                            # 将更新后的数据写回文件
                        with open(file_path, 'w', encoding='utf-8') as file:
                            dump(data, file, ensure_ascii=False, indent=4)
                    else:
                        print(f"用户【{user_name}】的提问无更新")