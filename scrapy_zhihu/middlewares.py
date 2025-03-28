from fake_useragent import UserAgent
from fake_useragent.errors import FakeUserAgentError
from random import choice


class RandomUserAgentMiddlware(object):
    """
    随机更换
    """
    def __init__(self, crawler):
        super(RandomUserAgentMiddlware, self).__init__()
        try:
            self.ua = UserAgent()
        except FakeUserAgentError:
            print('无法获取随机用户代理')
        # 可读取在settings文件中的配置，来决定开源库ua执行的方法，默认是random，也可是ie、Firefox等等
        self.ua_type = crawler.settings.get("RANDOM_UA_TYPE", "random")
        self.ip_list = crawler.settings.get("IP_LIST")

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    # 更换用户代理逻辑在此方法中
    def process_request(self, request, spider):
        def get_ua():
            return getattr(self.ua, self.ua_type)

        def get_ip():
            if not self.ip_list:
                return None
            return choice(self.ip_list)

        # 更换user-agent
        new_ua = get_ua()
        if new_ua:
            request.headers.setdefault('User-Agent', new_ua)
        # 更换ip代理
        new_ip = get_ip()
        if new_ip:
            request.meta['proxy'] = new_ip