import time

from utils import *
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
    scene_folder_path='tmp_scenes'
    if not os.path.exists(scene_folder_path):
        os.makedirs(scene_folder_path)
    video_path=st.session_state['raw_video_path']
    video_name=video_path.split('/')[-1].split('.')[0]
    video_folder_path=os.path.join(scene_folder_path,video_name)
    os.makedirs(video_folder_path,exist_ok=True)

    # 场景分割解析
    # min_scene_len=40,每个场景最少40帧
    # min_scene_len=
    scene_list = detect(video_path, ContentDetector(min_scene_len=40))

    # 保存切割结果
    # ffmpeg_arg = '-c:v libx264 -preset veryfast -crf 22 -c:a aac'
    # ffmpeg_arg = '-c:v copy -c:a copy'
    # split_video_ffmpeg(video_path, scene_list, video_name=video_name, show_progress=True, arg_override=ffmpeg_arg)
    video=open_video(st.session_state['raw_video_path'])
    save_images(scene_list,video,1,output_dir=video_folder_path,show_progress=True)

    # 展示关键帧
    scene_images = os.listdir(video_folder_path)
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
                    img_path=os.path.join(video_folder_path,scene_images[img_index])
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

