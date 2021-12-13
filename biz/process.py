from biz.datatype import Account
# from common import qr


def process_qrcode(account: Account):
    if len(account.wechat_id) > 0:
        account.qr_code = 'https://open.weixin.qq.com/qr/code?username=' + account.wechat_id