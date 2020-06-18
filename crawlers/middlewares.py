import requests


def get_proxy():
    return requests.get("http://127.0.0.1:5010/get/").json()


def delete_proxy(proxy):
    if proxy.startswith('http'):
        proxy = proxy[8:]

    requests.get("http://127.0.0.1:5010/delete/?proxy={}".format(proxy))


class ProxyMiddleware(object):

    def process_request(self, request, spider):
        if getattr(spider, 'name', None) in ('szse',):
            proxy = get_proxy().get('proxy')
            request.meta['proxy'] = 'http://{}'.format(proxy)
