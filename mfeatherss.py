import tornado.web
import tornado.httpclient
import tornado.ioloop
import lxml.etree
import re
import os

class MainHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        http = tornado.httpclient.AsyncHTTPClient()
        http.fetch(os.getenv("MFEATHERS_FEED"),
                callback=self.on_response)

    def on_response(self, response):
        if response.error: raise tornado.web.HTTPError(500)
        xml = lxml.etree.fromstring(response.body)
        items = xml.xpath('//item')
        for item in items:
            title = item.find('title')
            if title is not None and re.search(r'mfeathers:\s+@geepawhill\s+http', title.text, flags=re.I):
                title.text = title.text.split()[2]
            else:
                item.getparent().remove(item)
        self.set_header('Content-Type', 'application/rss+xml; charset=utf-8')
        self.write(lxml.etree.tostring(xml))
        self.finish()

application = tornado.web.Application([
    (r"/", MainHandler)
])

if __name__ == '__main__':
    application.listen(os.environ.get("PORT", 8888))
    tornado.ioloop.IOLoop.instance().start()
