import base64
import io
import matplotlib.dates as mdates
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from django.shortcuts import render
from pytrends.request import TrendReq


def index(request):
    if request.method == "GET":
        return render(request, "html/home.html")

    # フォームからデータがPOSTされた場合
    else:
        if request.POST.get("country", False) == "JP":
            pytrends = TrendReq(hl='ja-jp', tz=540)
        else:
            pytrends = TrendReq(hl='en-US')

        timeframes = ['today 5-y', 'today 12-m', 'today 3-m']
        cat = '0'
        geo = ''
        gprop = ''

        word1 = request.POST.get("word1", False)
        word2 = request.POST.get("word2", False)
        word3 = request.POST.get("word3", False)
        word4 = request.POST.get("word4", False)
        word5 = request.POST.get("word5", False)

        all_keywords = []
        if word1 != "":
            all_keywords.append(word1)
        if word2 != "":
            all_keywords.append(word2)
        if word3 != "":
            all_keywords.append(word3)
        if word4 != "":
            all_keywords.append(word4)
        if word5 != "":
            all_keywords.append(word5)

        # グラフ
        plt.figure(figsize=(10, 8))
        fontprop = FontProperties(fname='static/fonts/ipag.ttf')
        x_pos = np.arange(len(all_keywords))

        # Last 5-years
        pytrends.build_payload(
            all_keywords, cat, timeframes[0], geo, gprop)

        data = pytrends.interest_over_time()
        mean = data.mean()
        mean = round(mean / mean.max() * 100, 2)
        ax1 = plt.subplot2grid((3, 2), (0, 0), rowspan=1, colspan=1)
        ax2 = plt.subplot2grid((3, 2), (0, 1), rowspan=1, colspan=1)
        for kw in all_keywords:
            ax1.plot(data[kw], label=kw, )
        ax2.bar(x_pos, mean, align='center')
        plt.xticks(x_pos, all_keywords, font_properties=fontprop)

        # Last 12-months
        pytrends.build_payload(
            all_keywords, cat, timeframes[1], geo, gprop)

        data = pytrends.interest_over_time()
        mean = data.mean()
        mean = round(mean / mean.max() * 100, 2)
        ax3 = plt.subplot2grid((3, 2), (1, 0), rowspan=1, colspan=1)
        ax4 = plt.subplot2grid((3, 2), (1, 1), rowspan=1, colspan=1)
        for kw in all_keywords:
            ax3.plot(data[kw], label=kw)
        ax4.bar(x_pos, mean, align='center')
        plt.xticks(x_pos, all_keywords, font_properties=fontprop)

        # Last 3-months
        pytrends.build_payload(
            all_keywords, cat, timeframes[2], geo, gprop)

        data = pytrends.interest_over_time()
        mean = data.mean()
        mean = round(mean / mean.max() * 100, 2)
        ax5 = plt.subplot2grid((3, 2), (2, 0), rowspan=1, colspan=1)
        ax6 = plt.subplot2grid((3, 2), (2, 1), rowspan=1, colspan=1)
        for kw in all_keywords:
            ax5.plot(data[kw], label=kw)
        ax6.bar(x_pos, mean[0:len(all_keywords)], align='center')
        plt.xticks(x_pos, all_keywords, font_properties=fontprop)
        # 凡例など
        ax1.set_ylabel('Last 5 years')
        ax3.set_ylabel('Last year')
        ax5.set_ylabel('Last 3 months')
        ax1.set_title('Relative interest over time', fontsize=14)
        ax2.set_title('Relative average interest for the period', fontsize=14)
        ax3.xaxis.set_major_formatter(mdates.DateFormatter('%m-%y'))
        ax5.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m'))
        ax1.legend(prop=fontprop)
        ax3.legend(prop=fontprop)
        ax5.legend(prop=fontprop)

        # グラフをhtmlに描画するための設定
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        image_png = buffer.getvalue()
        graph = base64.b64encode(image_png)
        graph = graph.decode('utf-8')
        buffer.close()

        # 関連ワード
        pytrends.build_payload([word1], cat, timeframes[2], geo, gprop)
        data = pytrends.related_queries()
        top = data[word1]['top'].rename(
            columns={'query': 'word'}, index=lambda x: x+1)
        rising = data[word1]['rising'].rename(
            columns={'query': 'word'}, index=lambda x: x+1)

        # 急上昇ワード
        trending_jp = pytrends.trending_searches(
            'japan').rename(columns={0: 'word'}, index=lambda x: x+1)

        trending_us = pytrends.trending_searches(
            'united_states').rename(columns={0: 'word'}, index=lambda x: x+1)

        return render(
            request,
            "html/home.html",
            {"top": top.to_html,
                "rising": rising.to_html,
                "trending_jp": trending_jp.to_html,
                "trending_us": trending_us.to_html,
                "graph": graph
             },
        )
