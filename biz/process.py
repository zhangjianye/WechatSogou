from biz.datatype import Article
# from utilities import qr


def process_qrcode(articles: [Article]):
    # TODO: implement this asynchronously
    for article in articles:
        gzh = article.gzh
        if gzh and len(gzh.wechat_id) > 0:
            article.gzh.qr_code = 'https://open.weixin.qq.com/qr/code?username=' + gzh.wechat_id