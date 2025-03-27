import pandas as pd
import streamlit as st
import subprocess
import json
import os
import time
import glob
import jieba
import pickle
from pyecharts.charts import Bar, Pie, Scatter, HeatMap, WordCloud
from pyecharts import options as opts
from streamlit_echarts import st_pyecharts
from collections import defaultdict
from bs4 import BeautifulSoup

# 定义爬虫命令选项
# 添加更可靠的JavaScript监测代码

crawler_commands = {
    "爬取用户信息": {
        "func": 1,
        "file_template": "D:\\scrapy_zhihu\\data\\{user_name}.json"
    },
    "爬取关注者信息": {
        "func": 2,
        "file_template": "D:\\scrapy_zhihu\\data\\{user_name}_followees.json"
    },
    "爬取粉丝信息": {
        "func": 3,
        "file_template": "D:\\scrapy_zhihu\\data\\{user_name}_followers.json"
    },
    "爬取回答及评论信息": {
        "func": 4,
        "file_template": "D:\\scrapy_zhihu\\data\\{user_name}_answers\\1.json"
    },
    "爬取提问及回答信息": {
        "func": 5,
        "file_template": "D:\\scrapy_zhihu\\data\\{user_name}_questions\\1.json"
    },
    "重新爬取所有信息": {
        "func": 6,
        "file_template": None  # 特殊处理，需要检查多个文件
    },
    "自动更新回答和提问信息": {
        "func": 7,
        "file_template": None  # 特殊处理，需要检查多个文件
    }
}
def get_file_path(user_name, func_value):
    """根据功能号获取对应的文件路径"""
    for cmd in crawler_commands.values():
        if cmd["func"] == func_value:
            if cmd["file_template"]:
                return cmd["file_template"].format(user_name=user_name)
    return None

def check_file_update(file_path, last_modified_time=None):
    """
    检查文件是否更新
    :param file_path: 文件路径
    :param last_modified_time: 上次修改时间
    :return: (是否更新, 当前修改时间, 文件内容)
    """
    if not os.path.exists(file_path):
        return False, None, None
    
    current_mtime = os.path.getmtime(file_path)
    
    if last_modified_time is None or current_mtime > last_modified_time:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = json.load(f)
            return True, current_mtime, content
        except Exception as e:
            st.error(f"读取文件 {file_path} 失败: {e}")
            return False, current_mtime, None
    return False, current_mtime, None
def analyze_data(user_name):
    # 加载数据路径
    data_paths = {
        "followers": f"D:\\scrapy_zhihu\\data\\{user_name}_followers.json",
        "followees": f"D:\\scrapy_zhihu\\data\\{user_name}_followees.json",
        "answers": f"D:\\scrapy_zhihu\\data\\{user_name}_answers",
        "questions": f"D:\\scrapy_zhihu\\data\\{user_name}_questions"
    }
    
    # 加载停用词
    stopwords = set()
    if os.path.exists('./stopwords.txt'):
        with open('./stopwords.txt', 'r', encoding='utf-8') as f:
            stopwords = set(f.read().splitlines())
    
    # 加载数据
    def load_user_data(file_path):
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    followers = load_user_data(data_paths["followers"])
    followees = load_user_data(data_paths["followees"])
    
    # 数据处理函数
    def process_data(user_list):
        return {
            'gender': [u.get('gender', -1) for u in user_list],
            'names': [u.get('name', '') for u in user_list],
            'headlines': [u.get('headline', '') for u in user_list],
            'answer_counts': [u.get('answer_count', 0) for u in user_list],
            'follower_counts': [u.get('follower_count', 0) for u in user_list]
        }
    
    followers_data = process_data(followers)
    followees_data = process_data(followees)
    # 可视化分析
    st.header(f"{user_name}的数据分析结果")
    
    # 创建选项卡分开显示关注者和粉丝分析
    tab1, tab2, tab3, tab4 = st.tabs(["粉丝分析", "关注者分析", "用户回答分析", "用户提问分析"])
    
    with tab1:
        st.warning("如果图表未加载，请刷新页面或再次点击分析数据按钮。")
        st.subheader("粉丝数据分析")
        if followers:
            # 1. 粉丝性别分布
            st.markdown("### 1. 粉丝性别分布")
            gender_data = [
                ['男性', followers_data['gender'].count(1)],
                ['女性', followers_data['gender'].count(0)],
                ['未知', followers_data['gender'].count(-1)]
            ]
            
            col1, col2 = st.columns(2)
            with col1:
                pie = (
                    Pie(init_opts=opts.InitOpts(width="100%", height="400px"))
                    .add("", gender_data)
                    .set_global_opts(title_opts=opts.TitleOpts(title="粉丝性别分布",padding=[20, 0, 0, 110]))
                    .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c} ({d}%)"))
                )
                st_pyecharts(pie, height=400)
            
            with col2:
                bar = (
                    Bar(init_opts=opts.InitOpts(width="100%", height="400px"))
                    .add_xaxis([x[0] for x in gender_data])
                    .add_yaxis("数量", [x[1] for x in gender_data])
                    .set_global_opts(title_opts=opts.TitleOpts(title="粉丝性别分布柱状图",padding=[20, 0, 0, 90]))
                )
                st_pyecharts(bar, height=400)
            
            # 2. 粉丝的回答数量分布
            st.markdown("### 2. 粉丝的回答数量")
            answer_counts = followers_data['answer_counts']
            
            groups = {
                '0': answer_counts.count(0),
                '1-20': len([x for x in answer_counts if 1 <= x <= 20]),
                '21-50': len([x for x in answer_counts if 21 <= x <= 50]),
                '51-100': len([x for x in answer_counts if 51 <= x <= 100]),
                '>100': len([x for x in answer_counts if x > 100])
            }
            
            bar = (
                Bar(init_opts=opts.InitOpts(width="100%", height="400px"))
                .add_xaxis(list(groups.keys()))
                .add_yaxis("人数", list(groups.values()))
                .set_global_opts(title_opts=opts.TitleOpts(title="粉丝回答数量分布"))
            )
            st_pyecharts(bar, height=400)
            
            # 3. 粉丝的粉丝数量分布
            st.markdown("### 3. 粉丝的粉丝数量")
            follower_counts = followers_data['follower_counts']
            
            scatter_data = [[str(i), count] for i, count in enumerate(follower_counts) if count > 0]
            scatter = (
                Scatter(init_opts=opts.InitOpts(width="100%", height="400px"))
                .add_xaxis([x[0] for x in scatter_data])
                .add_yaxis("粉丝数", [x[1] for x in scatter_data])
                .set_global_opts(
                    title_opts=opts.TitleOpts(title="粉丝的粉丝数量分布"),
                    visualmap_opts=opts.VisualMapOpts(max_=max(follower_counts) if follower_counts else None)
                )
            )
            st_pyecharts(scatter, height=400)
            
            # 4. 粉丝个人简介关键词
            st.markdown("### 4. 粉丝个人简介关键词")
            headlines = [h for h in followers_data['headlines'] if h]
            
            word_freq = defaultdict(int)
            for text in headlines:
                words = jieba.cut(text)
                for word in words:
                    if word not in stopwords and len(word) > 1:
                        word_freq[word] += 1
            
            if word_freq:
                wordcloud_data = [[k, v] for k, v in sorted(word_freq.items(), key=lambda x: -x[1])[:50]]
                wordcloud = (
                    WordCloud(init_opts=opts.InitOpts(width="100%", height="400px"))
                    .add("", wordcloud_data, word_size_range=[10, 60])
                    .set_global_opts(title_opts=opts.TitleOpts(title="粉丝个人简介关键词"))
                )
                st_pyecharts(wordcloud, height=400)
            else:
                st.warning("没有可用的个人简介数据")
        else:
            st.warning("没有粉丝数据可供分析")

    # 在关注者分析选项卡中同样修改
    with tab2:
        st.warning("如果图表未加载，请刷新页面或再次点击分析数据按钮。")
        st.subheader("关注者数据分析")
        if followees:
            # 1. 关注者性别分布
            st.markdown("### 1. 关注者性别分布")
            gender_data = [
                ['男性', followees_data['gender'].count(1)],
                ['女性', followees_data['gender'].count(0)],
                ['未知', followees_data['gender'].count(-1)]
            ]
            
            col1, col2 = st.columns(2)
            with col1:
                pie = (
                    Pie(init_opts=opts.InitOpts(width="100%", height="400px"))
                    .add("", gender_data)
                    .set_global_opts(title_opts=opts.TitleOpts(title="关注者性别分布",padding=[20, 0, 0, 110]))
                    .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c} ({d}%)"))
                )
                st_pyecharts(pie, height=400)
            
            with col2:
                bar = (
                    Bar(init_opts=opts.InitOpts(width="100%", height="400px"))
                    .add_xaxis([x[0] for x in gender_data])
                    .add_yaxis("数量", [x[1] for x in gender_data])
                    .set_global_opts(title_opts=opts.TitleOpts(title="关注者性别分布柱状图",padding=[20, 0, 0, 90]))
                )
                st_pyecharts(bar, height=400)
            # 2. 关注者的回答数量分布
            st.markdown("### 2. 关注者的回答数量")
            answer_counts = followees_data['answer_counts']
            
            groups = {
                '0': answer_counts.count(0),
                '1-20': len([x for x in answer_counts if 1 <= x <= 20]),
                '21-50': len([x for x in answer_counts if 21 <= x <= 50]),
                '51-100': len([x for x in answer_counts if 51 <= x <= 100]),
                '>100': len([x for x in answer_counts if x > 100])
            }
        
            bar = (
                Bar(init_opts=opts.InitOpts(width="100%", height="400px"))
                .add_xaxis(list(groups.keys()))
                .add_yaxis("人数", list(groups.values()))
                .set_global_opts(title_opts=opts.TitleOpts(title="关注者回答数量分布"))
            )
            st_pyecharts(bar, height=400)
            # 3. 关注者的粉丝数量分布
            st.markdown("### 3. 关注者的粉丝数量")
            follower_counts = followees_data['follower_counts']
            
            scatter_data = [[str(i), count] for i, count in enumerate(follower_counts) if count > 0]
            scatter = (
                Scatter(init_opts=opts.InitOpts(width="100%", height="400px"))
                .add_xaxis([x[0] for x in scatter_data])
                .add_yaxis("粉丝数", [x[1] for x in scatter_data])
                .set_global_opts(
                    title_opts=opts.TitleOpts(title="关注者的粉丝数量分布"),
                    visualmap_opts=opts.VisualMapOpts(max_=max(follower_counts) if follower_counts else None)
                )
            )
            st_pyecharts(scatter, height=400)
           
            # 4. 关注者个人简介关键词
            st.markdown("### 4. 关注者个人简介关键词")
            headlines = [h for h in followees_data['headlines'] if h]
            
            word_freq = defaultdict(int)
            for text in headlines:
                words = jieba.cut(text)
                for word in words:
                    if word not in stopwords and len(word) > 1:
                        word_freq[word] += 1
            
            if word_freq:
                wordcloud_data = [[k, v] for k, v in sorted(word_freq.items(), key=lambda x: -x[1])[:50]]
                wordcloud = (
                    WordCloud()
                    .add("", wordcloud_data, word_size_range=[10, 60])
                    .set_global_opts(title_opts=opts.TitleOpts(title="关注者个人简介关键词"))
                )
                st_pyecharts(wordcloud)
            else:
                st.warning("没有可用的个人简介数据")
        else:
            st.warning("没有关注者数据可供分析")
    with tab3:
        st.warning("如果图表未加载，请刷新页面或再次点击分析数据按钮。")
        st.subheader("用户回答及评论词云分析")
        
        # 定义用户回答数据路径
        answers_dir = data_paths["answers"]
        
        if os.path.exists(answers_dir):
            # 获取最多10个回答文件
            answer_files = sorted(os.listdir(answers_dir))[:10]
            all_text = ""
            
            # 遍历每个回答文件
            for file in answer_files:
                file_path = os.path.join(answers_dir, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        answer_data = json.load(f)
                        
                        # 提取问题标题
                        all_text += answer_data.get('question', '') + " "
                        
                        # 提取回答内容（去除HTML标签）
                        content = answer_data.get('content', '')
                        if content:
                            soup = BeautifulSoup(content, 'html.parser')
                            all_text += soup.get_text() + " "
                        
                        # 提取评论内容
                        comments = answer_data.get('answer_comment', [])
                        for comment in comments:
                            comment_content = comment.get('comment_content', '')
                            if comment_content:
                                soup = BeautifulSoup(comment_content, 'html.parser')
                                all_text += soup.get_text() + " "
                
                except Exception as e:
                    st.warning(f"读取文件 {file} 时出错: {str(e)}")
                    continue
            
            if all_text.strip():
                # 中文分词处理
                word_freq = defaultdict(int)
                words = jieba.cut(all_text)
                for word in words:
                    if word not in stopwords and len(word) > 1:  # 过滤停用词和单字
                        word_freq[word] += 1
                
                if word_freq:
                    # 取前50个高频词
                    wordcloud_data = [[k, v] for k, v in sorted(word_freq.items(), key=lambda x: -x[1])[:50]]
                    
                    # 创建词云
                    wordcloud = (
                        WordCloud(init_opts=opts.InitOpts(width="100%", height="500px"))
                        .add("", wordcloud_data, word_size_range=[15, 80], shape='circle')
                        .set_global_opts(
                            title_opts=opts.TitleOpts(
                                title="用户回答及评论关键词分析",
                                pos_top="5%",
                                padding=[0, 0, 20, 0]
                            ),
                            tooltip_opts=opts.TooltipOpts(is_show=True)
                        )
                    )
                    st_pyecharts(wordcloud, height=500)
                    # 添加高频词表格展示
                    st.markdown("### 高频词统计")
                    df_words = pd.DataFrame(sorted(word_freq.items(), key=lambda x: -x[1])[:20], 
                                        columns=["关键词", "出现次数"])
                    st.dataframe(df_words)
                else:
                    st.warning("未能提取有效关键词")
            else:
                st.warning("没有可分析的文本内容")
        else:
            st.warning(f"未找到用户回答目录: {answers_dir}")
    with tab4:
        st.warning("如果图表未加载，请刷新页面或再次点击分析数据按钮。")
        st.subheader("用户提问及回答词云分析")
        
        # 定义用户提问数据路径
        questions_dir = f"D:\\scrapy_zhihu\\data\\{user_name}_questions"
        
        if os.path.exists(questions_dir):
            # 获取最多10个问题文件
            question_files = sorted(os.listdir(questions_dir))[:10]
            all_text = ""
            
            # 遍历每个问题文件
            for file in question_files:
                file_path = os.path.join(questions_dir, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        question_data = json.load(f)
                        
                        # 提取问题标题
                        all_text += question_data.get('question', '') + " "
                        
                        # 提取问题回答内容
                        answers = question_data.get('question_answer', [])
                        for answer in answers:
                            # 提取回答内容（去除HTML标签）
                            answer_content = answer.get('answer_content', '')
                            if answer_content:
                                soup = BeautifulSoup(answer_content, 'html.parser')
                                all_text += soup.get_text() + " "
                
                except Exception as e:
                    st.warning(f"读取文件 {file} 时出错: {str(e)}")
                    continue
            
            if all_text.strip():
                # 中文分词处理
                word_freq = defaultdict(int)
                words = jieba.cut(all_text)
                for word in words:
                    if word not in stopwords and len(word) > 1:  # 过滤停用词和单字
                        word_freq[word] += 1
                
                if word_freq:
                    # 取前50个高频词
                    wordcloud_data = [[k, v] for k, v in sorted(word_freq.items(), key=lambda x: -x[1])[:50]]
                    
                    # 创建词云
                    wordcloud = (
                        WordCloud(init_opts=opts.InitOpts(width="100%", height="500px"))
                        .add("", wordcloud_data, word_size_range=[15, 80], shape='circle')
                        .set_global_opts(
                            title_opts=opts.TitleOpts(
                                title="用户提问及回答关键词分析",
                                pos_top="5%",
                                padding=[0, 0, 20, 0]
                            ),
                            tooltip_opts=opts.TooltipOpts(is_show=True)
                        )
                    )
                    st_pyecharts(wordcloud, height=500)
                    
                    # 添加高频词表格展示
                    st.markdown("### 高频词统计")
                    df_words = pd.DataFrame(sorted(word_freq.items(), key=lambda x: -x[1])[:20], 
                                        columns=["关键词", "出现次数"])
                    st.dataframe(df_words)
                else:
                    st.warning("未能提取有效关键词")
            else:
                st.warning("没有可分析的文本内容")
        else:
            st.warning(f"未找到用户提问目录: {questions_dir}")
st.sidebar.title("导航")
page = st.sidebar.radio("选择页面", ["数据爬取", "数据分析"])
if page == "数据爬取":
# Streamlit 应用标题
    st.title("知乎爬虫控制面板")
    st.warning("第一次登录爬虫请先在命令行执行 scrapy crawl zhihu 命令，进入网页后会有登录提示，使用手动扫码/密码登录 登录成功后，回到命令行的输出区输入任意字符")
    # 输入用户名
    user_name = st.text_input("输入用户名", "廖雪峰")

    # 选择爬虫命令
    selected_command = st.selectbox("选择爬虫命令", list(crawler_commands.keys()))

    # 显示选择的命令
    st.write(f"你选择的命令是: {selected_command}")

    # 执行爬虫命令
    if st.button("执行爬虫"):
        # 启动 Chrome 浏览器
        chrome_data_dir = "D:\\scrapy_zhihu\\chrome_data"  # 修改为更简单的路径
        os.makedirs(chrome_data_dir, exist_ok=True)  # 确保目录存在

        chrome_command = [
            "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
            "--remote-debugging-port=9222",
            f"--user-data-dir={chrome_data_dir}",  # 去掉路径的引号
            "--no-first-run",
            "--headless",
            "--no-default-browser-check",
            "--disable-popup-blocking"
        ]
        
        try:
            # 启动 Chrome 浏览器
            chrome_process = subprocess.Popen(chrome_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            st.success("Chrome 浏览器启动成功！")
            
            # 等待 Chrome 启动完成
            time.sleep(1)  # 等待 5 秒，确保 Chrome 完全启动
            
            # 获取对应的 Scrapy 命令参数
            func_value = crawler_commands[selected_command]["func"]
            file_template = crawler_commands[selected_command]["file_template"]
            
            if func_value == 6:  # 重新爬取所有信息 - 检查所有文件
                files_to_check = [
                    get_file_path(user_name, 1),  # 用户信息
                    get_file_path(user_name, 2),  # 关注者
                    get_file_path(user_name, 3),  # 粉丝
                    get_file_path(user_name, 4),  # 回答
                    get_file_path(user_name, 5)   # 提问
                ]
                last_times = [os.path.getmtime(f) if f and os.path.exists(f) else None for f in files_to_check]
            elif func_value == 7:  # 自动更新回答和提问信息 - 只检查回答和提问
                files_to_check = [
                    get_file_path(user_name, 4),  # 回答
                    get_file_path(user_name, 5)   # 提问
                ]
                last_times = [os.path.getmtime(f) if f and os.path.exists(f) else None for f in files_to_check]
            else:  # 其他功能只检查对应的单个文件
                files_to_check = [get_file_path(user_name, func_value)]
                last_times = [os.path.getmtime(files_to_check[0]) if files_to_check[0] and os.path.exists(files_to_check[0]) else None]
                
                # 执行爬虫命令
            scrapy_command = [
                    "scrapy", "crawl", "zhihu",
                    "-a", f"user_name={user_name}",
                    "-a", f"func={func_value}"
                ]
                
            try:
                    result = subprocess.run(scrapy_command, capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        time.sleep(1)  # 等待文件写入
                        
                        updated_files = []
                        
                        # 功能4：展示answer文件夹下所有文件
                        if func_value == 4:
                            answer_dir = os.path.join("D:\\scrapy_zhihu\\data", f"{user_name}_answers")
                            if os.path.exists(answer_dir):
                                answer_files = glob.glob(os.path.join(answer_dir, "*.json"))
                                for file_path in answer_files:
                                    with open(file_path, 'r', encoding='utf-8') as f:
                                        content = json.load(f)
                                    updated_files.append((file_path, content))
                        
                        # 功能5：展示question文件夹下所有文件
                        elif func_value == 5:
                            question_dir = os.path.join("D:\\scrapy_zhihu\\data", f"{user_name}_questions")
                            if os.path.exists(question_dir):
                                question_files = glob.glob(os.path.join(question_dir, "*.json"))
                                for file_path in question_files:
                                    with open(file_path, 'r', encoding='utf-8') as f:
                                        content = json.load(f)
                                    updated_files.append((file_path, content))
                        
                        # 功能6：同时展示answer和question文件夹下所有文件
                        elif func_value == 6:
                            # 检查answer文件夹
                            user_file = get_file_path(user_name, 1)
                            if user_file and os.path.exists(user_file):
                                with open(user_file, 'r', encoding='utf-8') as f:
                                    content = json.load(f)
                                updated_files.append((user_file, content))
                            
                            # 检查关注者文件
                            followee_file = get_file_path(user_name, 2)
                            if followee_file and os.path.exists(followee_file):
                                with open(followee_file, 'r', encoding='utf-8') as f:
                                    content = json.load(f)
                                updated_files.append((followee_file, content))
                            
                            # 检查粉丝文件
                            follower_file = get_file_path(user_name, 3)
                            if follower_file and os.path.exists(follower_file):
                                with open(follower_file, 'r', encoding='utf-8') as f:
                                    content = json.load(f)
                                updated_files.append((follower_file, content))
                            
                            # 检查回答文件夹
                            answer_dir = os.path.join("D:\\scrapy_zhihu\\data", f"{user_name}_answers")
                            if os.path.exists(answer_dir):
                                answer_files = glob.glob(os.path.join(answer_dir, "*.json"))
                                for file_path in answer_files:
                                    with open(file_path, 'r', encoding='utf-8') as f:
                                        content = json.load(f)
                                    updated_files.append((file_path, content))
                            
                            # 检查提问文件夹
                            question_dir = os.path.join("D:\\scrapy_zhihu\\data", f"{user_name}_questions")
                            if os.path.exists(question_dir):
                                question_files = glob.glob(os.path.join(question_dir, "*.json"))
                                for file_path in question_files:
                                    with open(file_path, 'r', encoding='utf-8') as f:
                                        content = json.load(f)
                                    updated_files.append((file_path, content))
                        elif func_value == 7:
                            st.warning("自动更新模式已启动，将每隔30秒检查一次更新...")
                            
                            # 初始化 session_state
                            if 'auto_update_running' not in st.session_state:
                                st.session_state.auto_update_running = True
                            
                            # 创建停止按钮
                            if st.button("停止自动更新"):
                                st.session_state.auto_update_running = False
                            
                            # 初始化上次检查时间
                            last_check_times = {}
                            answer_dir = os.path.join("D:\\scrapy_zhihu\\data", f"{user_name}_answers")
                            question_dir = os.path.join("D:\\scrapy_zhihu\\data", f"{user_name}_questions")
                            
                            # 获取初始文件状态
                            def get_file_status(directory):
                                status = {}
                                if os.path.exists(directory):
                                    for file_path in glob.glob(os.path.join(directory, "*.json")):
                                        status[file_path] = os.path.getmtime(file_path)
                                return status
                            
                            last_answer_status = get_file_status(answer_dir)
                            last_question_status = get_file_status(question_dir)
                            
                            # 自动更新循环
                            while st.session_state.auto_update_running:
                                start_time = time.time()
                                
                                # 执行爬虫命令
                                scrapy_command = [
                                    "scrapy", "crawl", "zhihu",
                                    "-a", f"user_name={user_name}",
                                    "-a", f"func={func_value}"
                                ]
                                
                                try:
                                    result = subprocess.run(scrapy_command, capture_output=True, text=True)
                                    
                                    if result.returncode == 0:
                                        time.sleep(1)  # 等待文件写入
                                        
                                        # 获取当前文件状态
                                        current_answer_status = get_file_status(answer_dir)
                                        current_question_status = get_file_status(question_dir)
                                        
                                        # 检查回答文件更新
                                        updated_answers = []
                                        for file_path, mtime in current_answer_status.items():
                                            if file_path not in last_answer_status or mtime > last_answer_status[file_path]:
                                                updated_answers.append(file_path)
                                        
                                        # 检查提问文件更新
                                        updated_questions = []
                                        for file_path, mtime in current_question_status.items():
                                            if file_path not in last_question_status or mtime > last_question_status[file_path]:
                                                updated_questions.append(file_path)
                                        
                                        # 如果有更新
                                        if updated_answers or updated_questions:
                                            st.success("检测到内容更新！")
                                            
                                            # 显示所有回答文件
                                            if os.path.exists(answer_dir):
                                                st.subheader("回答内容：")
                                                answer_files = glob.glob(os.path.join(answer_dir, "*.json"))
                                                for file_path in answer_files:
                                                    is_updated = file_path in updated_answers
                                                    title = f"{'🔄 ' if is_updated else ''}回答 - {os.path.basename(file_path)}"
                                                    with st.expander(title):
                                                        with open(file_path, 'r', encoding='utf-8') as f:
                                                            st.json(json.load(f))
                                                        if is_updated:
                                                            st.success("此文件有新内容！")
                                            
                                            # 显示所有提问文件
                                            if os.path.exists(question_dir):
                                                st.subheader("提问内容：")
                                                question_files = glob.glob(os.path.join(question_dir, "*.json"))
                                                for file_path in question_files:
                                                    is_updated = file_path in updated_questions
                                                    title = f"{'🔄 ' if is_updated else ''}提问 - {os.path.basename(file_path)}"
                                                    with st.expander(title):
                                                        with open(file_path, 'r', encoding='utf-8') as f:
                                                            st.json(json.load(f))
                                                        if is_updated:
                                                            st.success("此文件有新内容！")
                                        
                                        # 更新最后检查状态
                                        last_answer_status = current_answer_status
                                        last_question_status = current_question_status
                                    
                                    else:
                                        st.error(f"爬虫执行失败: {result.stderr}")
                                
                                except Exception as e:
                                    st.error(f"执行爬虫命令时出错: {e}")
                                
                                # 等待30秒或直到停止
                                while time.time() - start_time < 30 and st.session_state.auto_update_running:
                                    time.sleep(1)
                            
                            st.success("自动更新已停止")
                            # 重置状态以便下次启动
                            st.session_state.auto_update_running = True

                        # 其他功能保持原有逻辑
                        else:
                            for i, file_path in enumerate(files_to_check):
                                if file_path:
                                    updated, mtime, content = check_file_update(file_path, last_times[i])
                                    if updated:
                                        updated_files.append((file_path, content))
                        
                        # 显示结果
                        if updated_files:
                            st.success(f"成功获取 {len(updated_files)} 个数据文件:")
                            for file_path, content in updated_files:
                                # 根据文件类型显示不同的标题
                                if "_answers" in file_path:
                                    title = f"回答数据 - {os.path.basename(file_path)}"
                                elif "_questions" in file_path:
                                    title = f"提问数据 - {os.path.basename(file_path)}"
                                elif "_followees" in file_path:
                                    title = "关注者列表"
                                elif "_followers" in file_path:
                                    title = "粉丝列表"
                                else:
                                    title = "用户基本信息"
                                
                                with st.expander(title):
                                    st.json(content)
                        else:
                            st.warning("爬虫执行成功，但未找到相关文件")
                    else:
                        st.error(f"爬虫执行失败: {result.stderr}")
            except Exception as e:
                        st.error(f"执行爬虫命令时出错: {e}")
            
            # 关闭 Chrome 浏览器
            chrome_process.terminate()
            st.success("Chrome 浏览器已关闭。")
            st.warning("注意：如果爬取数据不全或失败，请重新执行该命令或 使用 (重新爬取所有信息)命令。")
        except Exception as e:
            st.error(f"启动 Chrome 浏览器时出错: {e}")

elif page == "数据分析":
        st.title("知乎数据分析")
        user_name = st.text_input("输入要分析的用户名", "廖雪峰")
        if st.button("分析数据"):
            if user_name:
                analyze_data(user_name)
            else:
                st.warning("请输入用户名")