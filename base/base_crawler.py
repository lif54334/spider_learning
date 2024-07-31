from abc import ABC, abstractmethod
from typing import Dict, Optional

from playwright.async_api import BrowserContext, BrowserType

# 这个抽象类定义了一个爬虫的基本行为框架，包括启动爬虫、执行搜索以及启动浏览器的逻辑。
class AbstractCrawler(ABC):
    @abstractmethod
    async def start(self):
        # 定义了启动爬虫的入口点，具体实现应包含初始化、配置及启动爬取任务的逻辑。
        pass

    @abstractmethod
    async def search(self):
        # 抽象方法，定义了如何执行搜索操作，比如在网页上进行关键词搜索。
        pass

    @abstractmethod
    async def launch_browser(self, chromium: BrowserType, playwright_proxy: Optional[Dict], user_agent: Optional[str],
                             headless: bool = True) -> BrowserContext:
        # 启动一个带有特定配置的浏览器上下文，允许自定义代理、User-Agent、是否无头模式等。此方法为实际启动浏览器并创建浏览器上下文提供了统一的接口。
        pass

# 这个抽象类描述了用户登录的各种方式，适用于不同的平台和服务。
class AbstractLogin(ABC):
    @abstractmethod
    async def begin(self):
        # 开始登录过程的入口方法
        pass

    @abstractmethod
    async def login_by_qrcode(self):
        # 通过二维码扫描登录的抽象方法
        pass

    @abstractmethod
    async def login_by_mobile(self):
        # 通过手机号验证码登录的抽象方法
        pass

    @abstractmethod
    async def login_by_cookies(self):
        # 使用cookies直接登录的抽象方法
        pass

# 负责数据存储的抽象类，定义了如何存储抓取到的内容、评论和创作者信息。
class AbstractStore(ABC):
    @abstractmethod
    async def store_content(self, content_item: Dict):
        # 存储内容项，如帖子、文章等
        pass

    @abstractmethod
    async def store_comment(self, comment_item: Dict):
        # 存储评论数据
        pass

    # TODO support all platform
    # only xhs is supported, so @abstractmethod is commented
    @abstractmethod
    async def store_creator(self, creator: Dict):
        # 存储创作者信息，虽然这里注释掉了@abstractmethod，但暗示了未来可能需要为所有平台支持该功能
        pass

# 专注于图像存储的抽象类，目前仅注释说明了初步支持微博平台。
class AbstractStoreImage(ABC):
    # TODO: support all platform
    # only weibo is supported
    # @abstractmethod
    async def store_image(self, image_content_item: Dict):
        # 存储图像内容，预期用于处理从网页抓取的图像数据。
        pass

# 定义了一个通用的API客户端接口，用于发送HTTP请求及管理浏览器中的cookies。
class AbstractApiClient(ABC):
    @abstractmethod
    async def request(self, method, url, **kwargs):
        # 发起HTTP请求的方法，具体请求方式和URL由子类实现决定。
        pass

    @abstractmethod
    async def update_cookies(self, browser_context: BrowserContext):
        # 更新API客户端或相关服务的cookies，利用从浏览器上下文中获取的最新cookies，保持与浏览器会话的一致性。
        pass
