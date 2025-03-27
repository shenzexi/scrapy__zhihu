# scrapy__zhihu

## 一、简要介绍

结合scrapy开源爬虫框架，结合具体实际场景运用

大体采用DrissionPage（模拟浏览器行为） +  scrapy （request请求）进行爬取

其实可以用DrissionPage纯模拟，直接分析html文件，但是想直接获取json数据

而纯scrapy会被知乎的神秘请求参数ban掉

所以使用DrissionPage先模拟用户点击行为，先抓取相关查询API的流量包，将其header覆盖至自己的request请求，实现得到数据的json包，再进行数据处理和保存

### 实现功能

- 自动登录
- 爬取指定**重点**用户基本属性信息：用户名、性别、一句话介绍、居住地、所在行业、职业经历、个人简介
- 爬取指定**重点**用户社交关系：所有关注人和粉丝（如果关注人数量或者粉丝数量超过10，则只采集前10个），每个人的信息包括用户昵称、链接地址、回答问题数、文章数、关注者人数
- 爬取指定**重点**用户回答信息：前十条回答，每条回答包括问题、用户自身回答及其前十条评论
- 爬取指定**重点**用户提问信息：前十条提问，每条提问包括问题和前十条回答
- 自动更新提问和回答信息（30s）
- 对爬取信息进行可视化分析

### 功能展示

命令行执行

![image-20250327150935878](https://typora-1333264335.cos.ap-guangzhou.myqcloud.com/images/image-20250327150935878.png)

![image-20250327151418890](https://typora-1333264335.cos.ap-guangzhou.myqcloud.com/images/image-20250327151418890.png)

![image-20250327151653324](https://typora-1333264335.cos.ap-guangzhou.myqcloud.com/images/image-20250327151653324.png)

![image-20250327151846373](https://typora-1333264335.cos.ap-guangzhou.myqcloud.com/images/image-20250327151846373.png)

WEB前端展示视频
[![WEB前端](https://typora-1333264335.cos.ap-guangzhou.myqcloud.com/images/65b7bb2ce8dde27c6f92af2a49f802485740d6b4.jpg)](https://www.bilibili.com/video/BV1AtZGYxEMk/)
## 二、安装

1. 安装python库，建议使用conda创建虚拟环境，再使用requirement安装依赖

   ```
   conda create --name myenv python=3.11
   conda activate myenv
   pip install -r requirements.txt
   ```

## 三、使用

1. 命令行使用

```
usage: scrapy crawl zhihu_spider  [--user_name USER_NAME] [--func {1,2,3,4,5,6,7}]
  --user_name USER_NAME  要爬取的知乎用户名（默认：廖雪峰）
  --func {1,2,3,4,5,6,7}  功能选项：
                          1 - 查询用户信息（默认）
                          2 - 爬取用户关注列表
                          3 - 爬取用户粉丝列表
                          4 - 爬取用户回答
                          5 - 爬取用户提问
                          6 - 更新 headers 并重新爬取所有数据
                          7 - 自动更新回答和提问 

```

2.web界面使用

```
streamlit run scapy_crawler_ui.py //自动打开浏览器web界面
```

## 四、注意

1. 首次使用需要修改配置

   ```
   setting.py      
   	DOWNLOAD_PATH = "自己的数据保存地址"
   cookie.py
   	COOKIE_FILE = '浏览器登录Cookie保存地址'
   	prelogin()	chrome_driver = r'chrome驱动地址'
   #如果不能正常启动浏览器，使用下面命令
   "chrome驱动地址" --remote-debugging-port=9222 --user-data-dir="chrome数据保存地址（自己指定）"
   ```

   

2. 首次使用需要登录知乎（扫码/密码登录），然后关闭浏览器，重新启动程序

3. 如果出现爬取信息失败，请重新执行该命令，或者执行命令6

4. 分析数据前，请先爬取相关信息。如果分析数据不能正常展示，请刷新页面，再次执行分析数据命令
