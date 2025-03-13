import time

from utils import *
st.set_page_config(page_title="开始创作你的视频", page_icon="📈")
st.sidebar.header("▶️开始创作你的视频")

if "messages" not in st.session_state:
    st.session_state['messages']=[]
if "prompt_image_caption" not in st.session_state:
    st.session_state['prompt_image_caption']=open("prompts/prompt_img_caption.txt").read()
if "prompt_script_gen" not in st.session_state:
    st.session_state['prompt_script_gen']=open("prompts/prompt_script_gen.txt").read()

st.header("第一步: 输入需求",divider=True)
video_description=st.text_input(label="视频描述",value="请输入你的视频描述")
if "video_description" not in st.session_state:
    st.session_state['video_description']=video_description

image_list=st.file_uploader(label="上传产品图片",accept_multiple_files=True)
if "raw_image_list" not in st.session_state:
    image_infos={}
    for i,image in enumerate(image_list):
        image_infos[i]=image
    st.session_state["image_infos"]=image_infos

# 展示图片
num_img_per_row=3
image_infos=st.session_state["image_infos"]
keys=list(image_infos.keys())
row_num=len(image_infos)//num_img_per_row

if len(image_infos)%num_img_per_row!=0:
    row_num+=1
for i in range(row_num):
    with st.container():
        actual_col_num=min(num_img_per_row,len(keys)-i*num_img_per_row)
        for j,col in enumerate(st.columns(actual_col_num)):
            if i*num_img_per_row+j<len(keys):
                key=keys[i*num_img_per_row+j]
                col.write("[图片{}]".format(i*num_img_per_row+j))
                col.image(image_infos[key])
            else:
                break

if st.button(label="解析素材"):
    image_infos = st.session_state["image_infos"]
    keys = list(image_infos.keys())
    image_captions={}
    tmp_image_captions = {
        0: "这是一张展示一件毛衣的照片。毛衣的颜色是温暖的米白色，材质看起来柔软且略显蓬松，给人一种舒适的感觉。上面散布着一些细小的彩色点缀，颜色包括橙色、绿色和蓝色，这些点缀为整体淡色增添了活泼的元素。\n毛衣的设计是宽松的款式，白色的圆领显得简约而时尚。袖口和下摆都采用了螺纹编织的设计，增加了一定的弹性和贴合度。毛衣的整体剪裁流畅，给人一种轻松的休闲感。\n在照片中，一只手正从下方托起毛衣，手腕上有一个简单的金属手链，增添了几分优雅的气息。背景是明亮的白色墙面，光线柔和，使毛衣的颜色和质感得以更好地展示。整体呈现出一种温暖和舒适的氛围，适合秋冬季节穿着。",
        1: "这张图片展示了一位女性，身穿一件浅色的毛衣，具体来说是米白色。毛衣的款式为圆领，颜色干净，给人一种柔和的感觉。毛衣的领口和袖口处装饰有黑色的小圆点，这些点缀为简单的毛衣增添了一些时尚感和精致感。\n女性的手臂位置位于画面的右侧，手臂微微弯曲，做出一种轻松的姿势。她的手上戴着一只简单的银色手链，增加了一些细节。总体上，她的造型显得优雅且休闲。\n背景是一个简单的灰色墙面，与她的毛衣形成了一种协调的对比，使整体画面显得干净和简约。这种背景风格将重点放在了女性和她的服装上。\n图片中没有其他人物、动物或文字，集中展现了这位女性的服装特征和整体风格。"
    }
    if len(image_infos) % num_img_per_row != 0:
        row_num += 1
    for i in range(row_num):
        actual_col_num = min(num_img_per_row, len(keys) - i * num_img_per_row)
        if actual_col_num<=0:
            continue
        with st.container():
            for j, col in enumerate(st.columns(actual_col_num)):
                if i * num_img_per_row + j < len(keys):
                    key=keys[i * num_img_per_row + j]
                    image=image_infos[key]
                    time.sleep(4)
                    col.write("[图片{}]".format(i * num_img_per_row + j))
                    # 获取图片描述
                    # base64_image=encode_image_to_base64(image)
                    # prompt=st.session_state['prompt_image_caption']
                    # image_caption=call_multi_model_gpt(prompt,base64_image,image_mode='base64')
                    image_caption=tmp_image_captions[key]
                    col.write(image_caption)
                    image_captions[key]=image_caption
                else:
                    break
    if "image_captions" not in st.session_state:
        st.session_state["image_captions"]=image_captions


st.header("第二步: 生成剧本",divider=True)
clip_num = int(st.text_input(label="请输入镜头数",value=3))
if st.button("生成剧本"):
    video_description = st.session_state['video_description']
    image_captions=st.session_state['image_captions']
    prompt = st.session_state['prompt_script_gen'].replace('aaaaa', video_description).replace('bbbbb',json.dumps(image_captions))
    scripts = {
        '剧情梗概': "本视频展示了一款优雅舒适的女装毛衣，旨在传递温暖和时尚的气息。视频风格以写实为主，氛围和谐轻松，结合了柔和的色彩和轻音乐，突出毛衣的细腻设计和穿着效果。视频主要内容包括模特身着毛衣在不同场景下自然展现，体现毛衣的舒适感与时尚感。",
        "镜头": {
            "镜头1": {"时长": 5,
                      "镜头详细描述": "特写展示一件米白色毛衣，镜头缓缓拉近，聚焦于毛衣柔软的材质和细腻的编织纹理。光线柔和且温暖，背景为简单的白色墙面，营造出简约的氛围。",
                      "旁白": "这款毛衣以优雅的米白色为基调，搭配细腻的轻柔色点缀，给你带来极致的舒适感。",
                      "人物对话": "无"},
            "镜头2": {"时长": 4,
                      "镜头详细描述": "镜头切换至身穿毛衣的女性，微笑着站在窗边，阳光透过窗帘洒落在她身上，毛衣呈现出轻盈的感觉。她轻轻抚摸着毛衣，显示出对材质的喜爱。背景中可以隐约看到秋冬季节的风景。",
                      "旁白": "感受那种轻松自在的气息，适合在家中享受宁静时光。",
                      "人物对话": "模特轻声说:这件衣服真实太舒服了"},
            "镜头3": {"时长": 4,
                      "镜头详细描述": "中景展示女性在户外与朋友互动，穿着同款毛衣，轻松自然。她们相互嬉闹，营造出温馨的秋冬聚会气氛。背景是迷人的秋叶场景，光影交错，显得温暖而亲切。",
                      "旁白": "无论是闲适在家，还是出门游玩，都是冬日里的完美搭配", "人物对话": "无"}
        }
    }
    with st.chat_message("assistant"):
        # answer = st.write_stream(response_generator(prompt))
        # json_parsed_res = parse_json_response(answer)
        time.sleep(3)
        answer=st.write_stream(stream_data(json.dumps(scripts,ensure_ascii=False)))
        json_parsed_res=scripts
    st.session_state["messages"].append(['assistant', answer])
    st.session_state["script_gen_res"] = json_parsed_res
    st.text_area(label="剧情梗概",value=json_parsed_res["剧情梗概"])

    # 展示剧情
    for content_type in ['镜头名',"时长","镜头描述","旁白","人物对话"]:
        if clip_num%num_img_per_row!=0:
            row_num+=1
        for i in range(row_num):
            with st.container():
                for j,col in enumerate(st.columns(num_img_per_row)):
                    if i*num_img_per_row+j<clip_num:
                        key="镜头{}".format(i*num_img_per_row+j+1)
                        clip_info=json_parsed_res["镜头"][key]
                        if content_type=='镜头名':
                            col.write("[{}]".format(key))
                        elif content_type=='时长':
                            col.write("时长:{}s".format(clip_info['时长']))
                        elif content_type=='镜头描述':
                            col.write("[镜头描述]")
                            col.write(clip_info['镜头详细描述'])
                        elif content_type=='旁白':
                            col.write("[旁白]")
                            col.write(clip_info['旁白'])
                        elif content_type=='人物对话':
                            col.write("[人物对话]")
                            col.write(clip_info['人物对话'])
                    else:
                        break

st.header("第三步: 生成片段",divider=True)
if st.button("生成片段"):
    scripts=st.session_state['script_gen_res']
    keys=list(scripts['镜头'].keys())
    # 展示剧情
    for content_type in ['镜头名', "时长", "镜头描述","视频片段"]:
        if clip_num % num_img_per_row != 0:
            row_num += 1
        for i in range(row_num):
            actual_col_num = min(num_img_per_row, len(keys) - i * num_img_per_row)
            if actual_col_num<=0:
                continue
            with st.container():
                for j, col in enumerate(st.columns(actual_col_num)):
                    if i * num_img_per_row + j < clip_num:
                        key = "镜头{}".format(i * num_img_per_row + j + 1)
                        clip_info = scripts["镜头"][key]
                        # clip_info=json_parsed_res["镜头"][key]
                        if content_type == '镜头名':
                            col.write("[{}]".format(key))
                        elif content_type == '时长':
                            col.write("时长:{}s".format(clip_info['时长']))
                        elif content_type == '镜头描述':
                            col.write("[镜头描述]")
                            col.write(clip_info['镜头详细描述'])
                        elif content_type == '视频片段':
                            time.sleep(5)
                            video_path='tmp_videos/{}.mp4'.format(key)
                            if not os.path.exists(video_path):
                                video_path='tmp_videos/{}.mov'.format(key)
                            col.video(video_path)
                    else:
                        break


st.header("第四步: 检索音频",divider=True)

st.header("第五步: 合成视频",divider=True)