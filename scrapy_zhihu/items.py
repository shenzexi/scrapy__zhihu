from scrapy import Item, Field
class UserItem(Item):
    id = Field()
    name = Field()
    gender = Field()
    url_token = Field()
    locations = Field()
    IP_address = Field()
    business = Field()
    employments = Field()
    description = Field()
    educations = Field()
    headline = Field()
class AnswerItem(Item):
    answer_num = Field() #回答编号
    answer_time = Field() #回答时间
    question = Field() #问题
    content = Field() #回答内容
    voteup_count = Field() #点赞数  
    comment_count = Field() #评论数
    answer_url = Field()
    answer_id  = Field()
    answer_comment = Field()
class QuestionItem(Item):
    question_num = Field() #问题编号
    question_id = Field() #问题id
    question_url =  Field() #问题链接
    question_time = Field() #问题时间
    question = Field() #问题
    question_detail = Field() #问题详情
    answer_count = Field() #回答数
    question_answer = Field() #问题评论
class AnswerCommentItem(Item):
    answer_num = Field() #回答编号
    comment_num = Field()
    comment_id = Field() #评论人id
    comment_author = Field() #评论人昵称
    comment_time = Field() #评论时间
    comment_content = Field() #评论内容
    comment_voteup_count = Field() #评论点赞数
class QuestionAnswerItem(Item):
    question_num = Field()
    answer_num = Field()
    answer_id = Field() #评论人id
    answer_author = Field() #评论人昵称
    answer_time = Field() #评论时间    
    answer_content = Field() #评论内容
    answer_voteup_count = Field() #评论点赞数
    image_urls = Field()
class FolloweeItem(Item):
    name = Field()  # 用户昵称
    gender = Field()
    headline = Field()  # 个人签名
    url = Field()  # 个人主页链接
    answer_count = Field()  # 回答问题数
    articles_count = Field()  # 文章数
    follower_count = Field()  # 被关注者人数
class FollowerItem(Item):
    name = Field()  # 用户昵称
    gender = Field()  # 性别
    headline = Field()  # 个人简介
    url = Field()  # 个人主页链接
    answer_count = Field()  # 回答问题数
    articles_count = Field()  # 文章数
    follower_count = Field()  # 被关注者人数
    