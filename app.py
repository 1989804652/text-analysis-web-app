import streamlit as st
import requests
from bs4 import BeautifulSoup
import jieba
from collections import Counter
import pandas as pd
from pyecharts import options as opts
from pyecharts.charts import WordCloud, Bar, Pie, Line, Scatter, Funnel, Radar
from pyecharts.globals import SymbolType
from streamlit_echarts import st_pyecharts
import re

def get_text_content(url):
    """获取网页文本内容"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 移除script、style等标签
        for tag in soup.find_all(['script', 'style', 'iframe']):
            tag.decompose()
            
        return soup.get_text()
        
    except Exception as e:
        st.error(f"获取内容失败: {str(e)}")
        return ""

def process_text(text, min_freq=2):
    """文本分词和统计"""
    # 加载停用词
    stop_words = set([line.strip() for line in open('stop_words.txt', encoding='utf-8')])
    
    # 分词并过滤
    words = jieba.cut(text)
    words = [w for w in words if w not in stop_words and len(w) > 1]
    
    # 统计词频
    word_freq = Counter(words)
    
    # 过滤低频词
    word_freq = {k:v for k,v in word_freq.items() if v >= min_freq}
    
    return word_freq

def create_charts(word_freq):
    """创建各种图表"""
    # 检查是否有数据
    if not word_freq:
        st.error("没有找到任何词频数据，请确保文本内容不为空且分词正确")
        return {}
        
    # 准备数据
    items = list(word_freq.items())
    words, freqs = zip(*sorted(items, key=lambda x: x[1], reverse=True)[:20])
    
    charts = {
        "词云图": create_wordcloud(items),
        "柱状图": create_bar(words, freqs),
        "饼图": create_pie(words, freqs),
        "折线图": create_line(words, freqs),
        "散点图": create_scatter(words, freqs),
        "漏斗图": create_funnel(words, freqs),
        "雷达图": create_radar(words, freqs)
    }
    
    return charts

def create_wordcloud(items):
    """创建词云图"""
    c = (
        WordCloud()
        .add("", items, word_size_range=[20, 100], shape=SymbolType.DIAMOND)
        .set_global_opts(title_opts=opts.TitleOpts(title="词云图"))
    )
    return c

def create_bar(words, freqs):
    """创建柱状图"""
    c = (
        Bar()
        .add_xaxis(list(words))
        .add_yaxis("词频", list(freqs))
        .set_global_opts(
            title_opts=opts.TitleOpts(title="词频柱状图"),
            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=45))
        )
    )
    return c

def create_pie(words, freqs):
    """创建饼图"""
    c = (
        Pie()
        .add("", [list(z) for z in zip(words, freqs)])
        .set_global_opts(title_opts=opts.TitleOpts(title="词频饼图"))
    )
    return c

def create_line(words, freqs):
    """创建折线图"""
    c = (
        Line()
        .add_xaxis(list(words))
        .add_yaxis("词频", list(freqs))
        .set_global_opts(
            title_opts=opts.TitleOpts(title="词频趋势图"),
            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=45))
        )
    )
    return c

def create_scatter(words, freqs):
    """创建散点图"""
    c = (
        Scatter()
        .add_xaxis(list(words))
        .add_yaxis("词频", list(freqs))
        .set_global_opts(
            title_opts=opts.TitleOpts(title="词频散点图"),
            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=45))
        )
    )
    return c

def create_funnel(words, freqs):
    """创建漏斗图"""
    c = (
        Funnel()
        .add("词频", [list(z) for z in zip(words, freqs)])
        .set_global_opts(title_opts=opts.TitleOpts(title="词频漏斗图"))
    )
    return c

def create_radar(words, freqs):
    """创建雷达图"""
    c = (
        Radar()
        .add_schema(
            schema=[
                opts.RadarIndicatorItem(name=word, max_=max(freqs))
                for word in words[:8]  # 限制为前8个词，避免图表过于密集
            ]
        )
        .add("词频", [freqs[:8]])
        .set_global_opts(title_opts=opts.TitleOpts(title="词频雷达图"))
    )
    return c

def main():
    st.title("文本分析可视化工具")
    
    # 侧边栏
    st.sidebar.header("配置")
    url = st.sidebar.text_input("输入文章URL")
    min_freq = st.sidebar.slider("最小词频", 1, 10, 2)
    chart_type = st.sidebar.selectbox("选择图表类型", 
        ["词云图", "柱状图", "饼图", "折线图", "散点图", "漏斗图", "雷达图"])
    
    if url:
        text = get_text_content(url)
        if text:
            word_freq = process_text(text, min_freq)
            if word_freq:  # 检查是否有词频数据
                # 展示词频统计
                st.subheader("词频统计 (Top 20)")
                df = pd.DataFrame(
                    sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:20],
                    columns=["词语", "频次"]
                )
                st.dataframe(df)
                
                # 展示选中的图表
                st.subheader(f"可视化图表 - {chart_type}")
                charts = create_charts(word_freq)
                if charts:  # 确保有图表数据
                    st_pyecharts(charts[chart_type])
            else:
                st.warning("未能从文本中提取到有效词频数据")

if __name__ == "__main__":
    main()
