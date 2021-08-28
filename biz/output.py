from xlsxwriter import Workbook
from xlsxwriter.worksheet import Worksheet
from biz.datatype import Article, Account
from io import BytesIO
from urllib.request import urlopen
import os
import datetime


def output_excel(articles: [Article], filename, sheet_name):
    filename = __get_validated_filename(filename)
    workbook = Workbook(filename)
    sheet = workbook.add_worksheet(sheet_name)
    __prepare_header(sheet)
    __write_content(sheet, articles)
    workbook.close()


def __prepare_header(sheet: Worksheet):
    headers = ['图片URL', '标题', '发布时间', '微信名称', '是否加V', '微信号', '功能介绍', '账号主体', '二维码']
    for i, h in enumerate(headers):
        sheet.write(0, i, h)


def __write_content(sheet: Worksheet, articles: [Article]):
    sheet.set_default_row(51)
    row = 1
    for article in articles:
        # __write_image_by_url(sheet, row, 0, url)
        urls = '\n'.join(article.imgs)
        sheet.write(row, 0, urls)
        sheet.write(row, 1, article.title)
        sheet.write(row, 2, datetime.datetime.fromtimestamp(article.time).strftime('%Y-%m-%d %H:%M:%S'))
        sheet.write(row, 3, article.wechat_name)
        sheet.write(row, 4, '是' if article.isv == 1 else '否')
        gzh: Account = article.gzh
        sheet.write(row, 5, gzh.wechat_id)
        sheet.write(row, 6, gzh.desc)
        sheet.write(row, 7, gzh.principal)
        print('qr_code={}'.format(gzh.qr_code))
        if len(gzh.qr_code) > 0:
            __write_image_by_url(sheet, row, 8, gzh.qr_code)
        row += 1
    sheet.set_column(0, 0, 100)
    sheet.set_column(1, 1, 50)
    sheet.set_column(2, 3, 15)
    sheet.set_column(4, 4, 8)
    sheet.set_column(5, 5, 20)
    sheet.set_column(6, 6, 100)
    sheet.set_column(7, 7, 50)
    sheet.set_column(8, 8, 51)


def __write_image_by_url(sheet: Worksheet, row, col, url):
    image_data = BytesIO(urlopen(url).read())
    sheet.insert_image(row, col, url, {'image_data': image_data, 'x_scale': 0.5, 'y_scale': 0.5})


def __get_validated_filename(filename: str):
    if not os.path.isabs(filename):
        filename = os.path.join(os.getcwd(), filename)
    splits = os.path.splitext(filename)
    print(splits)
    if len(splits) < 2 or len(splits[1]) <= 1:
        filename += '.xlsx'
    splits = os.path.split(filename)
    path = splits[0]
    if not os.path.exists(path):
        os.makedirs(path)
    return filename
