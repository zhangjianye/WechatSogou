from xlsxwriter import Workbook
from xlsxwriter.worksheet import Worksheet
from biz.datatype import Article, Account
from io import BytesIO
from urllib.request import urlopen
import os
import datetime
import traceback


def prepare_excel(filename, sheet_name):
    filename = __get_validated_filename(filename)
    workbook = Workbook(filename)
    sheet = workbook.add_worksheet(sheet_name)
    __prepare_header(sheet)
    return workbook, sheet


def close_excel(workbook: Workbook):
    workbook.close()


def output_excel(workbook: Workbook, sheet: Worksheet, articles: [Article], start_row=0) -> int:
    next_start_row = __write_content(sheet, workbook, articles, start_row)
    return next_start_row


def __prepare_header(sheet: Worksheet):
    headers = ['编号', '图片URL', '标题', '发布时间', '微信名称', '是否加V', '微信号', '功能介绍', '账号主体', '二维码']
    for i, h in enumerate(headers):
        sheet.write(0, i, h)
    sheet.set_column(1, 1, 100)
    sheet.set_column(2, 2, 50)
    sheet.set_column(3, 4, 18)
    sheet.set_column(5, 5, 8)
    sheet.set_column(6, 6, 20)
    sheet.set_column(7, 7, 100)
    sheet.set_column(8, 8, 50)
    sheet.set_column_pixels(9, 9, 105)
    sheet.freeze_panes(1, 0)


def __write_content(sheet: Worksheet, workbook: Workbook, articles: [Article], start_row) -> int:
    # sheet.set_default_row(51)
    merge_format = workbook.add_format({'align': 'left', 'valign': 'vcenter'})
    row = start_row
    for article in articles:
        first_row = row
        col = 0
        try:
            # __write_image_by_url(sheet, row, 0, url)
            for index, img in enumerate(article.imgs):
                sheet.write(row, col, index + 1)
                sheet.write(row, col + 1, img)
                row += 1
            last_row = row - 1
            col += 2
            __write_maybe_merged_cell(sheet, first_row, col, last_row, col, article.title, merge_format)
            col += 1
            # sheet.write(first_row, 1, article.title)
            __write_maybe_merged_cell(sheet, first_row, col, last_row, col, datetime.datetime.fromtimestamp(article.time).strftime('%Y-%m-%d %H:%M:%S'), merge_format)
            col += 1
            # sheet.write(first_row, 2, datetime.datetime.fromtimestamp(article.time).strftime('%Y-%m-%d %H:%M:%S'))
            __write_maybe_merged_cell(sheet, first_row, col, last_row, col, article.wechat_name, merge_format)
            col += 1
            # sheet.write(first_row, 3, article.wechat_name)
            __write_maybe_merged_cell(sheet, first_row, col, last_row, col, '是' if article.isv == 1 else '否', merge_format)
            col += 1
            # sheet.write(first_row, 4, '是' if article.isv == 1 else '否')
            gzh: Account = article.gzh
            __write_maybe_merged_cell(sheet, first_row, col, last_row, col, gzh.wechat_id, merge_format)
            col += 1
            # sheet.write(first_row, 5, gzh.wechat_id)
            __write_maybe_merged_cell(sheet, first_row, col, last_row, col, gzh.desc, merge_format)
            col += 1
            # sheet.write(first_row, 6, gzh.desc)
            __write_maybe_merged_cell(sheet, first_row, col, last_row, col, gzh.principal, merge_format)
            col += 1
            # sheet.write(first_row, 7, gzh.principal)
            __write_maybe_merged_cell(sheet, first_row, col, last_row, col, None, merge_format)
            print('qr_code={}'.format(gzh.qr_code))
            if len(gzh.qr_code) > 0:
                __write_image_by_url(sheet, first_row, col, gzh.qr_code)
        except Exception as e:
            print('exception occured, e={}, article={}, imgs={}'.format(e, article, article.imgs))
            print(traceback.print_exc())
        # row += 1
    return row

def __write_maybe_merged_cell(sheet:Worksheet, first_row, first_col, last_row, last_col, data, format):
    if first_col != last_col or first_row != last_row:
        sheet.merge_range(first_row, first_col, last_row, last_col, data, format)
    else:
        sheet.write(first_row, first_col, data, format)


def __write_image_by_url(sheet: Worksheet, row, col, url):
    image_data = BytesIO(urlopen(url).read())
    sheet.insert_image(row, col, url, {'image_data': image_data, 'x_scale': 0.25, 'y_scale': 0.25})


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
