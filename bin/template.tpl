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
        .max{width:100%;height:auto;}
        .fixTableHead {
            overflow-y: auto;
            /*height: 210px;*/
        }
        .fixTableHead thead th {
            position: sticky;
            top: 0;
        }
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
    <script>
        $(function(){
            $('#img').click(function(){
                alert($(this).attr('src'))
                $(this).toggleClass('thumb');
                $(this).toggleClass('max');
            });
        });
    </script>
</head>

<body>
<div class="fixTableHead">
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
<!--        <tr>-->
<!--            <td class="number">0</td>-->
<!--            <td>-->
<!--                <img class="thumb" src="https://mmbiz.qpic.cn/mmbiz_jpg/6qmZLshELjJlcGtFT2IW5KsGDDDtxB0giaBTkm2uPfa57GBmUFGyB2h9pKkVQolTUzBcVUIoo4Ls4NdnUIaylTw/640?wx_fmt=jpeg&tp=webp&wxfrom=5&wx_lazy=1&wx_co=1">-->
<!--                <img class="thumb" src="http://mmbiz.qpic.cn/mmbiz/5bpM6vatbKzrnfLeFMun6RjEylB6VD4efXFGB4IzGLjFicP2AWyxQlibziaP7x7NraVdmcX4G1eo29Hn6MuXAXljQ/640?wx_fmt=png">-->
<!--                <img class="thumb" src="http://mmbiz.qpic.cn/mmbiz_jpg/WEoYcYvD3uY5sjKcV9WhBiaEibruhTOZuteN7y3kKX7c1SRBfSzxByy3XFrV3YNwQexAz8ib8QsUcoibSzN39mFlew/640?wx_fmt=jpeg">-->
<!--                <img class="thumb" src="http://mmbiz.qpic.cn/mmbiz_png/NgibPXAgsMHibUtwzdAcTD91XezaXAR7iauTI7ibDcaWicF8HFHx9VdUuckylicRx0XO8xYeSgnUjn3emvwcJmm8kKsw/640?wx_fmt=png">-->
<!--                <img class="thumb" src="http://mmbiz.qpic.cn/mmbiz_jpg/WEoYcYvD3uY5sjKcV9WhBiaEibruhTOZut7DX0mEjzk6ibicfmpnFYQpwcgV6iaKy5LyjE4CqzUElIpibXsofPyNPEjg/640?wx_fmt=jpeg">-->
<!--                <img class="thumb" src="http://mmbiz.qpic.cn/mmbiz_jpg/NgibPXAgsMHibUtwzdAcTD91XezaXAR7iaudYwT7rYThtC2qEXO0zyA2IaVGClicbgnG5XKTrJctzFsBfeDthp8uAA/640?wx_fmt=jpeg">-->
<!--                <img class="thumb" src="http://mmbiz.qpic.cn/mmbiz_jpg/dAcqSCBn0nbyG1oJM2LmPlDvXiaZvzlxlyLBSoOB4libI5xRJqOa46MvLktASVlcOiaCgxPcXOy8XicICBnIpzbkNA/0?wx_fmt=jpeg">-->
<!--                <img class="thumb" src="http://mmbiz.qpic.cn/mmbiz_jpg/WEoYcYvD3uY5sjKcV9WhBiaEibruhTOZutWicWlg2NZS4z2yEKFxyMsnNhZMNCRe6MWQvib2KPV1ywB0Bzc3E7D8lQ/640?wx_fmt=jpeg">-->
<!--                <img class="thumb" src="http://mmbiz.qpic.cn/mmbiz_jpg/NgibPXAgsMHibUtwzdAcTD91XezaXAR7iaudTN5EgEvEibVEpHJPiaXlJl6Xeicn24uwVMwU4uiasO7lqUHLvRqlMJRhQ/640?wx_fmt=jpeg">-->
<!--                <img class="thumb" src="http://mmbiz.qpic.cn/mmbiz/0y9ibmULDTbDWlEe7mmNNqPiaeZ4O7x1GQsnU3t6trd6q50w3fqDgIMIGib9rOszQyIicVsMy2r4fGurV5ibSKMhiaLg/0?">-->
<!--                <img class="thumb" src="http://mmbiz.qpic.cn/mmbiz/5bpM6vatbKzrnfLeFMun6RjEylB6VD4eU61sur0YRZvt3e39GJGXRmfBpG0hAfHyTD8xZXxJMmTHBHxibPTFmiaQ/640?wx_fmt=png">-->
<!--                <img class="thumb" src="http://mmbiz.qpic.cn/mmbiz_jpg/NgibPXAgsMHibUtwzdAcTD91XezaXAR7iauKbQVnvSaPOXxcAiaTSUovbpibh1Syxrs2VuRdTTIMDdpgHhKfSOrSfOA/640?wx_fmt=jpeg">-->
<!--                <img class="thumb" src="http://mmbiz.qpic.cn/mmbiz_jpg/NgibPXAgsMHibUtwzdAcTD91XezaXAR7iauNlXgmvEIOAIWgpxWqyK44NDKhDxMaG6FxMAUWpW8aPNDQhuCFcgH2w/640?wx_fmt=jpeg">-->
<!--                <img class="thumb" src="http://mmbiz.qpic.cn/mmbiz/5bpM6vatbKzrnfLeFMun6RjEylB6VD4eT22UIOK67FHNFTibgrsmSz8x8R3QiaIerASibRbBzhwGbsRLycS6stqfg/640?wx_fmt=png">-->
<!--                <img class="thumb" src="http://mmbiz.qpic.cn/mmbiz_gif/P3micZRzIkgT6u40YQf1GoCfxKZqY2Zk9b14MByCFe0mcuqIzODZIyCPrYmj4ibgJA0zlib5KW4ick2wheNEMFVP6A/0?wx_fmt=gif">-->
<!--                <img class="thumb" src="http://mmbiz.qpic.cn/mmbiz/5bpM6vatbKzrnfLeFMun6RjEylB6VD4eE7ebjPcdxaoxULMHVw3esyIaBicW7k958jSZSWECTMrufSZqgD85wkg/640?wx_fmt=png">-->
<!--            </td>-->
<!--            <td>【福利】免费送票!在嘉定体验舌尖上的动画,共赴食与爱的大冒险</td>-->
<!--            <td>2017-07-12 20:00:25</td>-->
<!--            <td>嘉定都市网</td>-->
<!--            <td>嘉定都市网</td>-->
<!--            <td>是</td>-->
<!--            <td>ijiading</td>-->
<!--            <td>上海嘉都文化传播有限公司</td>-->
<!--            <td>嘉定权威资讯平台、新鲜优惠信息集合、同城活动召集地、吃喝玩乐推荐站、潮流情报广播台、便民信息集合地。</td>-->
<!--            <td><img class="qrcode" src=""></td>-->
<!--        </tr>-->
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
<!--        <tr>-->
<!--            <td>1.2</td>-->
<!--            <td>2.2</td>-->
<!--            <td>3.2</td>-->
<!--        </tr>-->
<!--        <tr>-->
<!--            <td>1.3</td>-->
<!--            <td>2.3</td>-->
<!--            <td>3.3</td>-->
<!--        </tr>-->
<!--        <tr>-->
<!--            <td>1.4</td>-->
<!--            <td>2.4</td>-->
<!--            <td>3.4</td>-->
<!--        </tr>-->
<!--        <tr>-->
<!--            <td>1.5</td>-->
<!--            <td>2.5</td>-->
<!--            <td>3.5</td>-->
<!--        </tr>-->
<!--        <tr>-->
<!--            <td>1.5</td>-->
<!--            <td>2.5</td>-->
<!--            <td>3.5</td>-->
<!--        </tr>-->
<!--        <tr>-->
<!--            <td>1.5</td>-->
<!--            <td>2.5</td>-->
<!--            <td>3.5</td>-->
<!--        </tr>-->
<!--        <tr>-->
<!--            <td>1.5</td>-->
<!--            <td>2.5</td>-->
<!--            <td>3.5</td>-->
<!--        </tr>-->
<!--        <tr>-->
<!--            <td>1.5</td>-->
<!--            <td>2.5</td>-->
<!--            <td>3.5</td>-->
<!--        </tr>-->
<!--        <tr>-->
<!--            <td>1.5</td>-->
<!--            <td>2.5</td>-->
<!--            <td>3.5</td>-->
<!--        </tr>-->
<!--        <tr>-->
<!--            <td>1.5</td>-->
<!--            <td>2.5</td>-->
<!--            <td>3.5</td>-->
<!--        </tr>-->
<!--        <tr>-->
<!--            <td>1.5</td>-->
<!--            <td>2.5</td>-->
<!--            <td>3.5</td>-->
<!--        </tr>-->
<!--        <tr>-->
<!--            <td>1.5</td>-->
<!--            <td>2.5</td>-->
<!--            <td>3.5</td>-->
<!--        </tr>-->
<!--        <tr>-->
<!--            <td>1.5</td>-->
<!--            <td>2.5</td>-->
<!--            <td>3.5</td>-->
<!--        </tr>-->
<!--        <tr>-->
<!--            <td>1.5</td>-->
<!--            <td>2.5</td>-->
<!--            <td>3.5</td>-->
<!--        </tr>-->
<!--        <tr>-->
<!--            <td>1.5</td>-->
<!--            <td>2.5</td>-->
<!--            <td>3.5</td>-->
<!--        </tr>-->
<!--        <tr>-->
<!--            <td>1.5</td>-->
<!--            <td>2.5</td>-->
<!--            <td>3.5</td>-->
<!--        </tr>-->
<!--        <tr>-->
<!--            <td>1.5</td>-->
<!--            <td>2.5</td>-->
<!--            <td>3.5</td>-->
<!--        </tr>-->
<!--        <tr>-->
<!--            <td>1.5</td>-->
<!--            <td>2.5</td>-->
<!--            <td>3.5</td>-->
<!--        </tr>-->
<!--        <tr>-->
<!--            <td>1.5</td>-->
<!--            <td>2.5</td>-->
<!--            <td>3.5</td>-->
<!--        </tr>-->
<!--        <tr>-->
<!--            <td>1.5</td>-->
<!--            <td>2.5</td>-->
<!--            <td>3.5</td>-->
<!--        </tr>-->
<!--        <tr>-->
<!--            <td>1.5</td>-->
<!--            <td>2.5</td>-->
<!--            <td>3.5</td>-->
<!--        </tr>-->
<!--        <tr>-->
<!--            <td>1.5</td>-->
<!--            <td>2.5</td>-->
<!--            <td>3.5</td>-->
<!--        </tr>-->
<!--        <tr>-->
<!--            <td>1.5</td>-->
<!--            <td>2.5</td>-->
<!--            <td>3.5</td>-->
<!--        </tr>-->
<!--        <tr>-->
<!--            <td>1.5</td>-->
<!--            <td>2.5</td>-->
<!--            <td>3.5</td>-->
<!--        </tr>-->
<!--        <tr>-->
<!--            <td>1.5</td>-->
<!--            <td>2.5</td>-->
<!--            <td>3.5</td>-->
<!--        </tr>-->
<!--        <tr>-->
<!--            <td>1.5</td>-->
<!--            <td>2.5</td>-->
<!--            <td>3.5</td>-->
<!--        </tr>-->
<!--        <tr>-->
<!--            <td>1.5</td>-->
<!--            <td>2.5</td>-->
<!--            <td>3.5</td>-->
<!--        </tr>-->
<!--        <tr>-->
<!--            <td>1.5</td>-->
<!--            <td>2.5</td>-->
<!--            <td>3.5</td>-->
<!--        </tr>-->
<!--        <tr>-->
<!--            <td>1.5</td>-->
<!--            <td>2.5</td>-->
<!--            <td>3.5</td>-->
<!--        </tr>-->
<!--        <tr>-->
<!--            <td>1.5</td>-->
<!--            <td>2.5</td>-->
<!--            <td>3.5</td>-->
<!--        </tr>-->
<!--        <tr>-->
<!--            <td>1.5</td>-->
<!--            <td>2.5</td>-->
<!--            <td>3.5</td>-->
<!--        </tr>-->
<!--        <tr>-->
<!--            <td>1.5</td>-->
<!--            <td>2.5</td>-->
<!--            <td>3.5</td>-->
<!--        </tr>-->
<!--        <tr>-->
<!--            <td>1.5</td>-->
<!--            <td>2.5</td>-->
<!--            <td>3.5</td>-->
<!--        </tr>-->
<!--        <tr>-->
<!--            <td>1.5</td>-->
<!--            <td>2.5</td>-->
<!--            <td>3.5</td>-->
<!--        </tr>-->
<!--        <tr>-->
<!--            <td>1.5</td>-->
<!--            <td>2.5</td>-->
<!--            <td>3.5</td>-->
<!--        </tr>-->
<!--        <tr>-->
<!--            <td>1.5</td>-->
<!--            <td>2.5</td>-->
<!--            <td>3.5</td>-->
<!--        </tr>-->
<!--        <tr>-->
<!--            <td>1.5</td>-->
<!--            <td>2.5</td>-->
<!--            <td>3.5</td>-->
<!--        </tr>-->
<!--        <tr>-->
<!--            <td>1.5</td>-->
<!--            <td>2.5</td>-->
<!--            <td>3.5</td>-->
<!--        </tr>-->
<!--        <tr>-->
<!--            <td>1.5</td>-->
<!--            <td>2.5</td>-->
<!--            <td>3.5</td>-->
<!--        </tr>-->
<!--        <tr>-->
<!--            <td>1.5</td>-->
<!--            <td>2.5</td>-->
<!--            <td>3.5</td>-->
<!--        </tr>-->
<!--        <tr>-->
<!--            <td>1.5</td>-->
<!--            <td>2.5</td>-->
<!--            <td>3.5</td>-->
<!--        </tr>-->
<!--        <tr>-->
<!--            <td>1.5</td>-->
<!--            <td>2.5</td>-->
<!--            <td>3.5</td>-->
<!--        </tr>-->
        </tbody>

    </table>
</div>
</body></html>