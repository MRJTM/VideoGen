"""
剧本生成的app界面
"""
import json
import streamlit as st

page1 = st.Page("pages/1_☁️_项目简介.py")
page2 = st.Page("pages/2_📷_视频生成.py")
page3 = st.Page("pages/3_✂️_视频编辑.py")
page4 = st.Page("pages/4_▶️_爆款复制.py")

pg = st.navigation([page1, page2,page3,page4])
pg.run()