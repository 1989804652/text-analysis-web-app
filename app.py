import streamlit as st
import requests
from bs4 import BeautifulSoup
import jieba
from collections import Counter
import pandas as pd
import plotly.express as px
from pyecharts import options as opts
from pyecharts.charts import WordCloud, Bar, Pie
from streamlit_echarts import st_pyecharts

# 设置页面配置
st.set_page_config(
    page_title="文本分析可视化工具",
    page_icon="📊",
    layout="wide"
)

# 简化CSS样式，避免DOM操作冲突
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stApp {
        background-color: #f5f7f9;
    }
    h1 {
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .plot-container {
        background-color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

def get_text_content(url):
    """获取网页文本内容"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        
        if response.status_code != 200:
            st.error(f"获取内容失败: HTTP状态码 {response.status_code}")
            return ""
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 移除无关标签
        for tag in soup(['script', 'style', 'iframe']):
            tag.decompose()
            
        text = soup.get_text()
        
        if not text.strip():
            st.error("提取的文本内容为空")
            return ""
            
        return text
        
    except Exception as e:
        st.error(f"获取内容失败: {str(e)}")
        return ""

def process_text(text):
    """文本分词和统计"""
    try:
        # 分词
        words = jieba.cut(text)
        # 过滤单字词
        words = [w for w in words if len(w) > 1]
        
        # 统计词频
        word_freq = Counter(words)
        
        if not word_freq:
            st.error("未能提取到有效词频")
            return {}
            
        return word_freq
        
    except Exception as e:
        st.error(f"分词处理失败: {str(e)}")
        return {}

def create_visualizations(word_freq):
    """创建可视化图表"""
    if not word_freq:
        return
        
    # 准备数据
    items = list(word_freq.items())
    words, freqs = zip(*sorted(items, key=lambda x: x[1], reverse=True)[:20])
    df = pd.DataFrame({'词语': words, '频次': freqs})
    
    # 使用tabs替代columns，减少DOM操作
    tab1, tab2 = st.tabs(["词频统计", "词云图"])
    
    with tab1:
        # 柱状图
        fig = px.bar(df, x='词语', y='频次', title='词频分布')
        st.plotly_chart(fig, use_container_width=True)
        
    with tab2:
        # 词云图
        wordcloud = (
            WordCloud()
            .add("", items[:50], word_size_range=[20, 100])
            .set_global_opts(title_opts=opts.TitleOpts(title="词云图"))
        )
        st_pyecharts(wordcloud)

def main():
    st.title("文本分析可视化工具")
    
    # 使用单列布局，减少复杂的布局操作
    url = st.text_input("输入文章URL", placeholder="请输入网址...")
    
    if url:
        with st.spinner('正在获取文章内容...'):
            text = get_text_content(url)
            
        if text:
            with st.spinner('正在分析文本...'):
                word_freq = process_text(text)
                
            if word_freq:
                create_visualizations(word_freq)
    else:
        st.info('请输入要分析的文章URL')

if __name__ == "__main__":
    main()
