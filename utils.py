import streamlit as st
import os
import openai
from openai import OpenAI
from docx import Document
import json
import requests
import base64
import numpy as np
from io import BytesIO
from PIL import Image,ImageFont,ImageDraw
import wget

OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
OPENAI_BASE_URL = st.secrets["BASE_URL"]
MODEL_NAME = st.secrets["MODEL_NAME"]
os.environ['OPENAI_API_KEY'] =OPENAI_API_KEY
os.environ['OPENAI_BASE_URL'] =OPENAI_BASE_URL

persist_directory='text_persist'
collection_name='text_collection'

# model_name="gpt-4o-mini-2024-07-18"
# model_name='o1-mini-2024-09-12'

client = OpenAI(api_key=OPENAI_API_KEY,base_url=OPENAI_BASE_URL)

def load_file(file_path):
    doc = Document(file_path)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    docs = "\n".join(full_text)
    docs=docs[:40000]
    return docs

def response_generator(prompt=''):
    stream = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": 'user', "content": prompt}
        ],
        stream=True
    )
    return stream

def call_multi_model_gpt(prompt,image):
    if image.startswith("http"):
        image_url=image
    else:
        image_url=f"data:image/jpeg;base64,{image}"
    completion = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_url
                        }
                    }
                ]
            },
        ],
    )
    try:
        res=completion.choices[0].message.content
    except:
        res=""
    return res

def call_gpt_image_gen(prompt):
    response = client.images.generate(
        model="dall-e-3",
        prompt = prompt,
        size = "1024x1024",
        quality="standard",
        n=1,
    )
    return response.data[0].url
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

def call_gpt_text2audio_gen(text,speech_file_name):
    speech_folder_path='./tmp_audios'
    if not os.path.exists(speech_folder_path):
        os.makedirs(speech_folder_path)
    response = client.audio.speech.create(
        model='tts-1',
        voice='echo',
        input=text
    )
    audio_file_path=os.path.join(speech_folder_path,'{}.mp3'.format(speech_file_name))
    response.stream_to_file(audio_file_path)
    if os.path.exists(audio_file_path):
        return audio_file_path
    else:
        return None

def parse_json_response(response):
    raw_res=response
    if "```json" in raw_res and "```" in raw_res:
        res = raw_res.split("```json")[1].split("```")[0]
    else:
        res = raw_res
    res = res.replace('\n', '').replace(' ', '')
    res = json.loads(res, strict=False)
    return res

def url_to_np_array(image_url):
    try:
        # 发送 HTTP 请求下载图片
        response = requests.get(image_url)
        response.raise_for_status()  # 确保请求成功

        # 使用 BytesIO 将下载的图片数据转换为可读的文件对象
        image_data = BytesIO(response.content)

        # 使用 PIL 打开图片
        image = Image.open(image_data)

        # 将图片转换为 NumPy 数组
        np_array = np.array(image)

        return np_array
    except Exception as e:
        print(f"Error: {e}")
        return None

# 将图片下载到本地，并返回本地路径
def download_image(image_url,img_name=None):
    # 从 URL 中提取文件名
    if img_name:
        filename = img_name
    else:
        if '?' in image_url:
            image_url = image_url.split('?')[0]
        filename = image_url.split("/")[-1]
    local_path = os.path.join('tmp_images', filename)
    if not os.path.exists('tmp_images'):
        os.makedirs('tmp_images')
    try:
        # 下载图片
        if not os.path.exists(local_path):
            wget.download(image_url, local_path)
        return local_path
    except Exception as e:
        print(f"Error: {e}")
        try:
            cmd=f'wget {image_url} -O {local_path}'
            os.system(cmd)
            return local_path
        except Exception as e:
            return None

def compute_resolution(resolution,ratio):
    w_r,h_r=ratio.split(':')
    w_r=float(w_r)
    h_r=float(h_r)
    res=int(resolution[:-1])
    if w_r>=h_r:
        width = res
        height=res/w_r*h_r
    else:
        height=res
        width=res/h_r*w_r
    return width,height

def crop_and_resize_img(img_path,target_width,target_height):
    img=Image.open(img_path)
    # 获取原始图片的宽度和高度
    original_width, original_height = img.size

    # 计算目标长宽比
    target_ratio = target_width / target_height
    original_ratio = original_width / original_height

    # 根据长宽比决定裁剪方式
    if original_ratio > target_ratio:
        # 原始图片比目标更宽，需要裁剪宽度
        new_width = int(original_height * target_ratio)
        left = (original_width - new_width) // 2
        upper = 0
        right = left + new_width
        lower = original_height
    else:
        # 原始图片比目标更高，需要裁剪高度
        new_height = int(original_width / target_ratio)
        left = 0
        upper = (original_height - new_height) // 2
        right = original_width
        lower = upper + new_height

    # 裁剪图片
    cropped_img = img.crop((left, upper, right, lower))
    # 调整大小到目标分辨率
    resized_img = cropped_img.resize((int(target_width), int(target_height)))
    return resized_img

def split_subtitle(text,audio_duration):
    parts=[]
    part=''
    total_len=0
    for word in text:
        if word not in ["，",",",".","。","!","！","?","？",":","："]:
            part+=word
        else:
            parts.append([part,len(part)])
            total_len+=len(part)
            part=""

    # 计算每段文字的时长
    new_parts=[]
    for p in parts:
        duration=float(audio_duration*p[1])/total_len
        new_parts.append([p[0],p[1],duration])
    return new_parts

def render_text_on_image(text,font_path,image,line_font_num=12,max_line_num=3):
    width,height=image.size
    new_image=image.copy()
    font_size=int(float(width)*0.9/line_font_num)
    lines=[]
    line=""
    for w in text:
        line=line+w
        if len(line)>=line_font_num:
            lines.append(line)
            line=""
    if len(line):
        lines.append(line)

    draw=ImageDraw.Draw(new_image)
    font = ImageFont.truetype(font_path, font_size)
    line_height = font.getbbox("测试")[3]
    y_position = int(height) - line_height*3-10
    for line in lines:
        text_width = font.getbbox(line)[2]
        x_position = (width - text_width) // 2
        draw.text((x_position, y_position), line, font=font, fill="white")
        y_position += line_height

    return new_image
