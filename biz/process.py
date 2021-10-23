from biz.datatype import Article
# from common import qr


def process_qrcode(articles: [Article]):
    for article in articles:
        gzh = article.gzh
        if gzh and len(gzh.wechat_id) > 0:
            article.gzh.qr_code = 'https://open.weixin.qq.com/qr/code?username=' + gzh.wechat_id