import streamlit as st

st.set_page_config(
    page_title="简介",
    page_icon="👋",
)

st.write("# Magic Gen! 👋")

st.sidebar.success("请选择上面一个功能")

st.markdown(
    """
    ## 简介
    Magic Gen 是一个面向创作者的视频生成和编辑的工具，让每个人成为专业的短视频工作者
    #### 功能1：视频生成
    我们提供了输入你的文字需求和素材，我们将帮你生成专业的短视频剧本，并基于剧本，生成视频片段，最后合成专业的视频
    #### 功能2：视频编辑
    我们提供了强大的视频编辑功能箱，通过AI，赋能你专业级的视频编辑能力
    """
)