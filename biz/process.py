from biz.datatype import Article
from utilities import qr


def process_qrcode(articles: [Article]):
    # TODO: implement this asynchronously
    for article in articles:
        qr_code = article.gzh.qr_code
        if len(qr_code) > 0:
            article.gzh.qr_code = 'http://qr.kegood.com/?m=1&e=Q&p=10&url=' + qr.decode_from_url(qr_code)