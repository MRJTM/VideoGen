# 导入requests包
import requests
# 此处仅提供一个简单的示例，具体实现起来方案有很多，可按需开发
def python_demo(img_path=''):
    url = 'https://s1.a2k6.com/mrjtm007/api/upload/'
    api_token = '973115c87ee3753cf44e'
    files = {'uploadedFile': ('demo.jpg', open(img_path, 'rb'), "image/jpeg")}
    data = {'api_token': api_token,
            'upload_format':'file', # 可选值 file 、base64 或者 url，不填则默认为file
            'mode': '1',
            'watermark': '0',
            }
    res = requests.post(url, data=data, files=files)
    print(res.status_code)
    print(res.json())
    print(res.json()['url'])

img_path='tmp_images/产品图7.jpg'
python_demo(img_path)