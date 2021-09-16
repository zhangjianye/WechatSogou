<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <script src="https://code.jquery.com/jquery-1.3.2.min.js" integrity="sha256-yDcKLQUDWenVBazEEeb0V6SbITYKIebLySKbrTp2eJk=" crossorigin="anonymous"></script>
    <script type="text/javascript">
        $('img.thumb').css({cursor: 'pointer'}).live('click', function () {
            let img = $(this);
            let bigImg = $('<img />').css({
                'max-width': '100%',
                'max-height': '100%',
                'display': 'block',
                'margin': 'auto',
                'align-self': 'center'
            });
            bigImg.attr({
                src: img.attr('src'),
                alt: img.attr('alt'),
                title: img.attr('title')
            });
            var over = $('<div />').text(' ').css({
                'height': '100%',
                'width': '100%',
                'background': 'rgba(0,0,0,.82)',
                'position': 'fixed',
                'top': 0,
                'left': 0,
                'opacity': 0.0,
                'cursor': 'zoom-out',
                'z-index': 9999,
                'text-align': 'center',
                'display': 'flex',
                'justify-content': 'center'
            }).append(bigImg).bind('click', function () {
                $(this).fadeOut(300, function () {
                    $(this).remove();
                });
            }).insertAfter(this).animate({
                'opacity': 1
            }, 300);
        });
    </script>
    <title>{{title}}</title>
    <style>
        table {
            border-collapse: collapse;
            width: 100%;
        }
        th,
        td {
            padding: 2px 2px;
            font-size: 12px;
            border: 1px solid #529432;
        }
        th {
            padding: 1px 1px;
            font-size: 14px;
            background: #ABDD93;
        }
        th.number {
            width: 40px;
        }
        th.img {
            width: 612px;
        }
        th.title {
            width: 200px;
        }
        th.time {
            width: 110px;
        }
        th.name {
            width: 100px;
        }
        th.v {
            width: 40px;
        }
        th.wechat-id {
            width: 150px;
        }
        th.principal {
            width: 200px;
        }
        th.desc {
            width: 400px;
        }
        th.qr-code {
            width: 100px;
        }
        td.number {
            text-align: right;
            padding-right: 10px;
        }
        td.isv {
            text-align: center;
        }
        img.thumb {
            max-width: 100px;
            max-height: 100px;
            width: auto;
            height: auto;
            cursor: zoom-in;
            margin: auto;
        }
        img.qrcode {
            width: 50px;
            height: 50px;
        }
        div.thumb_container {
            height: 100px;
            width: 100px;
            float: left;
            border: 1px solid darkcyan;
            display: flex;
            justify-content: center;
        }
        div.qrcode_container {
            width: 100%;
            height: 100%;
            display: flex;
        }
    </style>
</head>

<body>
    <table>
        <thead>
        <tr>
            <th class="number">编号</th>
            <th class="img">图片</th>
            <th class="title">标题</th>
            <th class="time">发布时间</th>
            <th class="name">公众号名称</th>
            <th class="name">公众号正式名称</th>
            <th class="v">加V</th>
            <th class="wechat-id">微信号</th>
            <th class="principal">账号主体</th>
            <th class="desc">功能介绍</th>
            <th class="qr-code">二维码</th>
        </tr>
        </thead>

        <tbody>
        % for article in articles:
            <tr>
                <td class="number">{{article['number']}}</td>
                <td>
                    % for img in article['images']:
                    <div class="thumb_container"><img class="thumb" src="{{img}}"></div>
                    % end
                </td>
                <td>{{article['title']}}</td>
                <td>{{article['time']}}</td>
                <td>{{article['wechat_name']}}</td>
                <td>{{article['gzh_name']}}</td>
                <td class="isv">{{article['isv']}}</td>
                <td>{{article['wechat_id']}}</td>
                <td>{{article['principal']}}</td>
                <td>{{article['desc']}}</td>
                <td><div class="qrcode_container"><img class="thumb qrcode" src="{{article['qr_code']}}"></div></td>
            </tr>
        % end
        </tbody>
    </table>
</body></html>