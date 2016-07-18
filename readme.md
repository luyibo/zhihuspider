#scrapy经验
authorspider中：
最开始看了网上的代码，
    #!/usr/bin/env python
    # -*- coding:utf-8 -*-
    from scrapy.contrib.spiders import CrawlSpider, Rule
    from scrapy.selector import Selector
    from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
    from scrapy.http import Request, FormRequest
    from zhihu.items import ZhihuItem



    class ZhihuSipder(CrawlSpider) :
        name = "zhihu"
        allowed_domains = ["www.zhihu.com"]
        start_urls = [
            "http://www.zhihu.com"
        ]
        rules = (
            Rule(SgmlLinkExtractor(allow = ('/question/\d+#.*?', )), callback = 'parse_page', follow = True),
            Rule(SgmlLinkExtractor(allow = ('/question/\d+', )), callback = 'parse_page', follow = True),
        )
        headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip,deflate",
        "Accept-Language": "en-US,en;q=0.8,zh-TW;q=0.6,zh;q=0.4",
        "Connection": "keep-alive",
        "Content-Type":" application/x-www-form-urlencoded; charset=UTF-8",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36",
        "Referer": "http://www.zhihu.com/"
        }

        #重写了爬虫类的方法, 实现了自定义请求, 运行成功后会调用callback回调函数
        def start_requests(self):
            return [Request("https://www.zhihu.com/login", meta = {'cookiejar' : 1}, callback = self.post_login)]

        #FormRequeset出问题了
        def post_login(self, response):
            print 'Preparing login'
            #下面这句话用于抓取请求网页后返回网页中的_xsrf字段的文字, 用于成功提交表单
            xsrf = Selector(response).xpath('//input[@name="_xsrf"]/@value').extract()[0]
            print xsrf
            #FormRequeset.from_response是Scrapy提供的一个函数, 用于post表单
            #登陆成功后, 会调用after_login回调函数
            return [FormRequest.from_response(response,   #"http://www.zhihu.com/login",
                                meta = {'cookiejar' : response.meta['cookiejar']},
                                headers = self.headers,  #注意此处的headers
                                formdata = {
                                '_xsrf': xsrf,
                                'email': '1095511864@qq.com',
                                'password': '123456'
                                },
                                callback = self.after_login,
                                dont_filter = True
                                )]

        def after_login(self, response) :
            for url in self.start_urls :
                yield self.make_requests_from_url(url)

        def parse_page(self, response):
            problem = Selector(response)
            item = ZhihuItem()
            item['url'] = response.url
            item['name'] = problem.xpath('//span[@class="name"]/text()').extract()
            print item['name']
            item['title'] = problem.xpath('//h2[@class="zm-item-title zm-editable-content"]/text()').extract()
            item['description'] = problem.xpath('//div[@class="zm-editable-content"]/text()').extract()
            item['answer']= problem.xpath('//div[@class=" zm-editable-content clearfix"]/text()').extract()
            return item`
但是现在知乎修改了登录方式，需要验证码，于是在这个代码的基础上加入了验证码功能，加入后发现使用make_request_from_url无法爬取数据，
显示500代码。查了很多资料最后终于发现需要在settings中加入USER_AGENT，但是加入后虽然现实200代码，但是仍然无法爬取数据，
使用了各种方法都无效，网上也没有找到相应的方法，最后加入了
`def parse(self,response):
    print response.body`
发现尽管前面已经登录，但是返回的页面还是登录页面，也就是说仍然需要登录，这就很尴尬了。最后

`def after_login(self, response):
        return [Request('https://www.zhihu.com',
                       headers = self.headers,
                       meta = {'cookiejar':1},
                       callback = self.parse,
                        dont_filter=True)]`
后成功了。


7.12更新:
由于昨天使用了10个进程爬虫，导致知乎反爬虫，研究了好久，包括了ip池，最后发现是settings中的USER_AGENT没有设置。


