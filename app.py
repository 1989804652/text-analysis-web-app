import streamlit as st
import requests
from bs4 import BeautifulSoup
import jieba
from collections import Counter
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from pyecharts import options as opts
from pyecharts.charts import (
    WordCloud, Bar, Pie, Funnel, 
    Radar, Scatter, Line
)
from streamlit_echarts import st_pyecharts

# 设置页面配置
st.set_page_config(
    page_title="文本分析可视化工具",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
st.markdown("""
    <style>
    /* 全局样式 */
    .main {
        background-color: #f8f9fa;
        padding: 2rem;
    }
    
    /* 标题样式 */
    h1 {
        color: #2c3e50;
        font-size: 2.5rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 2rem;
        padding: 1rem;
        background: linear-gradient(120deg, #84fab0 0%, #8fd3f4 100%);
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    h2 {
        color: #34495e;
        font-size: 1.8rem;
        margin-top: 2rem;
        border-left: 5px solid #2ecc71;
        padding-left: 1rem;
    }
    
    /* 卡片容器样式 */
    .stCard {
        background-color: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
        transition: transform 0.3s ease;
    }
    
    .stCard:hover {
        transform: translateY(-5px);
    }
    
    /* 数据框样式 */
    .dataframe {
        width: 100%;
        border-collapse: collapse;
        margin: 1rem 0;
        background-color: white;
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    
    .dataframe th {
        background-color: #2ecc71;
        color: white;
        padding: 1rem;
        text-align: left;
    }
    
    .dataframe td {
        padding: 0.8rem;
        border-bottom: 1px solid #eee;
    }
    
    /* 侧边栏样式 */
    .css-1d391kg {
        background-color: #ffffff;
        padding: 2rem;
        border-right: 1px solid #e1e4e8;
    }
    
    /* 输入框样式 */
    .stTextInput input {
        border-radius: 8px;
        border: 2px solid #e1e4e8;
        padding: 0.5rem;
        transition: border-color 0.3s ease;
    }
    
    .stTextInput input:focus {
        border-color: #2ecc71;
        box-shadow: 0 0 0 2px rgba(46, 204, 113, 0.2);
    }
    
    /* 滑块样式 */
    .stSlider div[data-baseweb="slider"] {
        height: 0.5rem;
    }
    
    .stSlider [data-testid="stThumbValue"] {
        background-color: #2ecc71;
    }
    
    /* 图表容器样式 */
    .plot-container {
        background-color: white;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* 标签页样式 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: white;
        border-radius: 10px;
        padding: 0.5rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding: 0 16px;
        background-color: transparent;
        border: none;
        color: #2c3e50;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: rgba(46, 204, 113, 0.1);
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #2ecc71 !important;
        color: white !important;
        border-radius: 8px;
    }
    
    /* 按钮样式 */
    .stButton button {
        background-color: #2ecc71;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton button:hover {
        background-color: #27ae60;
        transform: translateY(-2px);
    }
    
    /* 警告和错误消息样式 */
    .stAlert {
        border-radius: 10px;
        border: none;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    
    /* 度量值样式 */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        color: #2ecc71;
    }
    
    /* 工具提示样式 */
    .tooltip {
        background-color: white;
        border-radius: 8px;
        padding: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* 响应式布局调整 */
    @media (max-width: 768px) {
        .main {
            padding: 1rem;
        }
        
        h1 {
            font-size: 2rem;
        }
        
        .stCard {
            padding: 1rem;
        }
    }
    </style>
""", unsafe_allow_html=True)

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

def create_visualizations(word_freq):
    """创建三种不同库的可视化图表"""
    if not word_freq:
        st.error("没有找到任何词频数据")
        return
        
    # 准备数据
    items = list(word_freq.items())
    words, freqs = zip(*sorted(items, key=lambda x: x[1], reverse=True)[:20])
    df = pd.DataFrame({'词语': words, '频次': freqs})
    
    # 1. Plotly 可视化
    st.subheader("Plotly 可视化")
    
    # 柱状图
    fig_bar = px.bar(df, x='词语', y='频次', title='词频分布（Plotly）')
    fig_bar.update_layout(xaxis_tickangle=45)
    st.plotly_chart(fig_bar)
    
    # 饼图
    fig_pie = px.pie(df, values='频次', names='词语', title='词频占比（Plotly）')
    st.plotly_chart(fig_pie)
    
    # 2. Matplotlib 可视化
    st.subheader("Matplotlib 可视化")
    
    # 设置中文字体
    plt.style.use('classic')
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    
    # 水平柱状图
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(words[:10], freqs[:10])
    ax.set_title('Top 10 词频分布（Matplotlib）')
    ax.invert_yaxis()
    st.pyplot(fig)
    
    # 3. Pyecharts 可视化
    st.subheader("Pyecharts 可视化")
    
    # 词云图
    wordcloud = (
        WordCloud()
        .add("", items[:50], word_size_range=[20, 100])
        .set_global_opts(title_opts=opts.TitleOpts(title="词云图（Pyecharts）"))
    )
    st_pyecharts(wordcloud)
    
    # 带有涟漪效果的散点图
    scatter = (
        Scatter()
        .add_xaxis(list(words))
        .add_yaxis("词频", list(freqs))
        .set_global_opts(
            title_opts=opts.TitleOpts(title="词频散点图（Pyecharts）"),
            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=45))
        )
    )
    st_pyecharts(scatter)

def create_matplotlib_charts(words, freqs):
    """创建 Matplotlib 可视化图表"""
    # 使用 matplotlib 内置的样式 'classic' 替换 'seaborn'
    plt.style.use('classic')  
    
    # 设置中文字体
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    
    # 创建图表
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # 创建水平柱状图
    bars = ax.barh(words[:10], freqs[:10], color='skyblue')
    
    # 设置标题和标签
    ax.set_title('Top 10 词频分布（Matplotlib）')
    ax.set_xlabel('频次')
    ax.set_ylabel('词语')
    
    # 反转y轴，使最高频的词在顶部
    ax.invert_yaxis()
    
    # 添加网格线
    ax.grid(True, linestyle='--', alpha=0.3)
    
    # 为每个柱子添加数值标签
    for i, bar in enumerate(bars):
        width = bar.get_width()
        ax.text(width, bar.get_y() + bar.get_height()/2,
                f'{int(width)}',
                ha='left', va='center', fontsize=10)
    
    # 调整布局
    plt.tight_layout()
    
    # 在Streamlit中显示图表
    st.pyplot(fig)

def create_pyecharts_charts(words, freqs, items):
    """创建 Pyecharts 可视化图表"""
    # 1. 词云图
    wordcloud = (
        WordCloud()
        .add(
            series_name="",
            data_pair=items[:50],
            word_size_range=[20, 100],
            textstyle_opts=opts.TextStyleOpts(font_family="Microsoft YaHei"),
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title="词云图"),
            tooltip_opts=opts.TooltipOpts(is_show=True),
        )
    )
    st_pyecharts(wordcloud, height="400px")

    # 2. 柱状图
    bar = (
        Bar()
        .add_xaxis(list(words[:15]))
        .add_yaxis("词频", list(freqs[:15]))
        .set_global_opts(
            title_opts=opts.TitleOpts(title="柱状图"),
            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=45)),
            datazoom_opts=[opts.DataZoomOpts()],
        )
    )
    st_pyecharts(bar, height="400px")

    # 3. 饼图
    pie = (
        Pie()
        .add(
            "",
            [list(z) for z in zip(words[:10], freqs[:10])],
            radius=["40%", "75%"],
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title="饼图"),
            legend_opts=opts.LegendOpts(orient="vertical", pos_left="left")
        )
    )
    st_pyecharts(pie, height="400px")

    # 4. 漏斗图
    from pyecharts.charts import Funnel
    funnel = (
        Funnel()
        .add(
            "词频",
            [list(z) for z in zip(words[:10], freqs[:10])],
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title="漏斗图"),
        )
    )
    st_pyecharts(funnel, height="400px")

    # 5. 雷达图
    from pyecharts.charts import Radar
    radar_data = [[freq] for freq in freqs[:8]]
    radar_indicators = [{"name": word, "max": max(freqs)} for word in words[:8]]
    radar = (
        Radar()
        .add_schema(schema=radar_indicators)
        .add("词频", radar_data)
        .set_global_opts(
            title_opts=opts.TitleOpts(title="雷达图"),
        )
    )
    st_pyecharts(radar, height="400px")

    # 6. 散点图
    from pyecharts.charts import Scatter
    scatter = (
        Scatter()
        .add_xaxis(list(range(len(words[:20]))))
        .add_yaxis("词频", freqs[:20])
        .set_global_opts(
            title_opts=opts.TitleOpts(title="散点图"),
            xaxis_opts=opts.AxisOpts(
                type_="value",
                axislabel_opts=opts.LabelOpts(formatter="{value}"),
            ),
        )
    )
    st_pyecharts(scatter, height="400px")

    # 7. 折线图
    from pyecharts.charts import Line
    line = (
        Line()
        .add_xaxis(list(words[:20]))
        .add_yaxis(
            "词频",
            list(freqs[:20]),
            markpoint_opts=opts.MarkPointOpts(data=[
                opts.MarkPointItem(type_="max", name="最大值"),
                opts.MarkPointItem(type_="min", name="最小值"),
            ]),
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title="折线图"),
            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=45)),
        )
    )
    st_pyecharts(line, height="400px")

    # 8. 面积图
    from pyecharts.charts import Line
    area = (
        Line()
        .add_xaxis(list(words[:20]))
        .add_yaxis(
            "词频",
            list(freqs[:20]),
            areastyle_opts=opts.AreaStyleOpts(opacity=0.5),
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title="面积图"),
            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=45)),
        )
    )
    st_pyecharts(area, height="400px")

def main():
    # 页面标题
    st.markdown("""
        <h1>📊 文本分析可视化工具</h1>
        <div class='stCard'>
            <p style='text-align: center; color: #666;'>
                一个强大的文本分析工具，支持多种可视化方式展示文本特征
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # 创建两列布局
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.markdown("""
            <div class='stCard'>
                <h3 style='color: #2c3e50; margin-bottom: 1rem;'>配置参数</h3>
        """, unsafe_allow_html=True)
        
        url = st.text_input("输入文章URL", placeholder="请输入要分析的文章网址...")
        min_freq = st.slider("最小词频", 1, 10, 2)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # 添加使用说明
        with st.expander("使用说明 📖"):
            st.markdown("""
                1. 输入要分析的文章URL
                2. 调整最小词频阈值
                3. 查看不同形式的可视化结果
                4. 可以通过图表交互获取详细信息
            """)
    
    with col2:
        if url:
            text = get_text_content(url)
            if text:
                word_freq = process_text(text, min_freq)
                if word_freq:
                    # 数据概览
                    st.markdown("""
                        <div class='stCard'>
                            <h3 style='color: #2c3e50; margin-bottom: 1rem;'>数据概览</h3>
                    """, unsafe_allow_html=True)
                    
                    # 显示基本统计信息
                    col_stats1, col_stats2, col_stats3 = st.columns(3)
                    with col_stats1:
                        st.metric("不同词语数量", len(word_freq))
                    with col_stats2:
                        st.metric("总词频", sum(word_freq.values()))
                    with col_stats3:
                        st.metric("平均词频", round(sum(word_freq.values())/len(word_freq), 2))
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    # 创建可视化
                    create_visualizations(word_freq)
                else:
                    st.warning("未能从文本中提取到有效词频数据")
            else:
                st.error("获取文章内容失败，请检查URL是否正确")
        else:
            # 显示欢迎信息
            st.markdown("""
                <div class='stCard' style='text-align: center;'>
                    <h2 style='color: #2c3e50;'>👋 欢迎使用文本分析工具</h2>
                    <p style='color: #7f8c8d; font-size: 1.2rem;'>
                        请在左侧输入文章URL开始分析
                    </p>
                </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
