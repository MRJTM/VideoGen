import time
from moviepy.editor import ImageClip,CompositeVideoClip,AudioFileClip,TextClip,concatenate_videoclips,VideoFileClip
from utils import *
import random
from scenedetect import detect, ContentDetector,split_video_ffmpeg,save_images,open_video
st.set_page_config(page_title="开始创作你的视频", page_icon="📈")
st.sidebar.header("▶️开始创作你的视频")

if "messages" not in st.session_state:
    st.session_state['messages']=[]
if "prompt_image_caption" not in st.session_state:
    st.session_state['prompt_image_caption']=open("prompts/prompt_img_caption.txt").read()
if "prompt_script_gen" not in st.session_state:
    st.session_state['prompt_script_gen']=open("prompts/prompt_script_gen.txt").read()

st.header("第一步: 上传爆款",divider=True)
video_path=st.file_uploader(label="上传爆款视频",accept_multiple_files=False)
if video_path is not None:
    # 保存到本地
    file_name = video_path.name
    # 定义保存路径（可以根据需要修改路径）
    video_folder_path= 'tmp_videos'
    if not os.path.exists(video_folder_path):
        os.makedirs(video_folder_path)
    save_path = os.path.join(video_folder_path, file_name)  # 假设有一个 "uploads" 文件夹
    if not os.path.exists(save_path):
        with open(save_path, "wb") as f:
            f.write(video_path.getvalue())
    if os.path.exists(save_path):
        if 'raw_video_path' not in st.session_state:
            st.session_state['raw_video_path']=save_path

    st.video(save_path)

st.header("第二步: 获取关键帧",divider=True)
if st.button("获取关键帧"):
    video_path=st.session_state['raw_video_path']
    frame_folder_path = get_key_frames(video_path)

    # 展示关键帧
    scene_images = os.listdir(frame_folder_path)
    scene_images.sort()

    num_img_per_row = 3
    row_num = len(scene_images) // num_img_per_row
    scene_info={}

    if len(scene_images) % num_img_per_row != 0:
        row_num += 1
    for i in range(row_num):
        with st.container():
            actual_col_num = min(num_img_per_row, len(scene_images) - i * num_img_per_row)
            for j, col in enumerate(st.columns(actual_col_num)):
                img_index=i * num_img_per_row + j
                if  img_index< len(scene_images):
                    scene_key="镜头{:0>3d}".format(img_index+1)
                    col.write(scene_key)
                    img_path=os.path.join(frame_folder_path,scene_images[img_index])
                    col.image(img_path)
                    scene_info[scene_key]=img_path
                else:
                    break
    st.session_state['scene_info']=scene_info

st.header("第三步: 生成片段",divider=True)
if 'scene_info' in st.session_state:
    scene_info=st.session_state['scene_info']
    scene_keys = list(scene_info.keys())
else:
    scene_info={}
    scene_keys=['镜头1']


scene_keys.sort()
scene_key=st.selectbox(label="选择一个镜头",options=scene_keys,index=0)
if scene_key in scene_info:
    scene_img_path=scene_info[scene_key]
    st.session_state['scene_img_path']=scene_img_path
else:
    scene_img_path=None

target_image=st.file_uploader(label="上传参考图片",accept_multiple_files=False)

left,right=st.columns(2)
with left:
    st.write("参考镜头")
    if scene_img_path is not None:
        st.image(scene_img_path)
with right:
    st.write("目标商品")
    if target_image is not None:
        st.image(target_image)
        file_name = target_image.name
        # 定义保存路径（可以根据需要修改路径）
        image_folder_path = 'tmp_images'
        os.makedirs(image_folder_path, exist_ok=True)
        target_image_path = os.path.join(image_folder_path, file_name)
        if not os.path.exists(target_image_path):
            with open(target_image_path, "wb") as f:
                f.write(target_image.getvalue())
        st.session_state['target_image_path'] = target_image_path

prompt = st.text_input(label="输入你的描述")
time_len=st.radio(label="时长(单位:秒)",options=["4","8"],index=0,horizontal=True)
resolution=st.radio(label="分辨率(8s不支持1080p)",options=["480p","720p","1080p"],index=0,horizontal=True)
movement_amplitude=st.radio(label="运动幅度",options=["auto","small","medium","large"],index=0,horizontal=True)
aspect_ratio=st.radio(label="宽高比",options=["16:9","9:16","1:1"],index=0,horizontal=True)

if st.button("生成片段"):
    # 产生image urls
    image_urls=[]
    img_keys=['scene_img_path','target_image_path']
    for img_key in img_keys:
        if img_key in st.session_state:
            img_url=upload_img_to_url(st.session_state['scene_img_path'])
            image_urls.append(img_url)
        else:
            continue
    if len(image_urls)<len(img_keys):
        st.write("请上传参考图片")
    else:
        rsp=send_video_generation_request(prompt,image_urls,time_len,resolution,movement_amplitude,aspect_ratio)
        task_id=rsp['task_id']
        # task_id='797048627599011840'
        st.write("任务ID:{}".format(task_id))
        # 不断检查有没有成功，如果成功了，就下载视频，并显示结果
        progress_text = "视频生成中，请耐性等待"
        max_try_num=100
        my_bar = st.progress(max_try_num, text=progress_text)
        try_num=1
        video_url=""

        while len(video_url)==0 and try_num<max_try_num:
            time.sleep(1)
            check_res=check_video_gen_status(task_id)
            # st.write("check_res:{}".format(check_res))
            if len(check_res):
                if 'url' in check_res[0]:
                    video_url=check_res[0]['url']
            my_bar.progress(try_num,text=progress_text)
            try_num+=1
        if try_num==max_try_num or len(video_url)==0:
            st.write("生成视频失败")
        else:
            # 下载视频
            local_video_path='tmp_videos/{}.mp4'.format(scene_key)
            if os.path.exists(local_video_path):
                os.unlink(local_video_path)
            wget.download(video_url,local_video_path)
            st.video(local_video_path)


st.header("第四步: 合并片段",divider=True)
video_paths = [
        'tmp_videos/镜头001 (1).mp4',
        'tmp_videos/镜头031.mp4',
        'tmp_videos/镜头029.mp4',
    ]
# 展示多段视频
num_img_per_row = 3
row_num = len(video_paths) // num_img_per_row
scene_info = {}

if len(video_paths) % num_img_per_row != 0:
    row_num += 1
for i in range(row_num):
    with st.container():
        actual_col_num = min(num_img_per_row, len(video_paths) - i * num_img_per_row)
        for j, col in enumerate(st.columns(actual_col_num)):
            img_index = i * num_img_per_row + j
            if img_index < len(video_paths):
                video_path=video_paths[img_index]
                col.video(video_path)
            else:
                break

if st.button("合并片段"):
    # 合并视频
    video_paths = [
        'tmp_videos/镜头001 (1).mp4',
        'tmp_videos/镜头031.mp4',
        'tmp_videos/镜头029.mp4',
    ]
    video_clips = []
    for video_path in video_paths:
        video_clip = VideoFileClip(video_path)
        video_clips.append(video_clip)
    final_clip = concatenate_videoclips(video_clips)

    # 获取bgm
    audio_names=os.listdir('tmp_audios')
    audio_path_list=[os.path.join('tmp_audios',audio_name) for audio_name in audio_names]
    audio_clip=AudioFileClip(random.choice(audio_path_list))

    # 处理音频和视频时长不一致的情况
    video_duration = final_clip.duration
    audio_duration = audio_clip.duration
    if audio_duration > video_duration:
        # 音频时长大于视频时长：截断音频
        audio_clip = audio_clip.subclip(0, video_duration)
    elif audio_duration < video_duration:
        # 音频时长小于视频时长：复制音频
        audio_clips = []
        while audio_duration < video_duration:
            audio_clips.append(audio_clip)
            audio_duration += audio_clip.duration
        # 如果复制后的音频总时长仍然小于视频时长，再复制一次
        if audio_duration < video_duration:
            audio_clips.append(audio_clip.subclip(0, video_duration - audio_duration))
    final_clip=final_clip.set_audio(audio_clip)

    # 保存最终的视频
    final_video_path="tmp_videos/final_video.mp4"
    final_clip.write_videofile(final_video_path, codec="libx264", fps=24)
    st.video(final_video_path)
    pass

st.header("第五步: 生成标题",divider=True)
if st.button("解析视频镜头"):
    # 先对合成的视频进行抽帧
    video_path = "tmp_videos/final_video.mp4"
    frame_folder_path = get_key_frames(video_path)
    # 展示关键帧
    scene_images = os.listdir(frame_folder_path)
    scene_images.sort()
    num_img_per_row = 3
    row_num = len(scene_images) // num_img_per_row
    scene_info = {}
    image_paths = [os.path.join(frame_folder_path,frame_name) for frame_name in scene_images]
    st.session_state['image_paths']=image_paths

if 'image_paths' in st.session_state:
    image_paths=st.session_state['image_paths']
    if len(image_paths) % num_img_per_row != 0:
        row_num += 1
    for i in range(row_num):
        with st.container():
            actual_col_num = min(num_img_per_row, len(image_paths) - i * num_img_per_row)
            if actual_col_num>0:
                for j, col in enumerate(st.columns(actual_col_num)):
                    img_index = i * num_img_per_row + j
                    if img_index < len(image_paths):
                        scene_key = "镜头{:0>3d}".format(img_index + 1)
                        col.write(scene_key)
                        img_path=image_paths[img_index]
                        col.image(img_path)
                    else:
                        break

product_info=st.text_input(label="输入产品核心信息")
if st.button("生成标题"):
    # 结合用户输入的产品信息，组织prompt
    prompt_tmp=open("prompts/prompt_title_generation.txt").read()
    prompt=prompt_tmp.replace('aaaaa',product_info)

    # 调用gpt，产生标题信息
    image_paths=st.session_state['image_paths']
    raw_title_res=call_multi_model_gpt(prompt,image_paths,image_mode='local_path')
    title_res=parse_json_response(raw_title_res)

    # 打印标题信息
    with st.chat_message("assistant"):
        st.write(raw_title_res)

    for i in range(5):
        st.write("【标题{}】: {}".format(i+1,title_res['广告标题'][i]))

    # with st.chat_message("assistant"):
    #     answer = st.write_stream(response_generator(prompt))
