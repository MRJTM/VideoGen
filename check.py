import requests

task_id='797048627599011840'
api_key='vda_2683281298413230_IaL6zdK5jpWCdOsrI4bILoo62ca9jMQ0'
# 定义 API 的 URL 和请求头
api_url = f"https://api.vidu.cn/ent/v2/tasks/{task_id}/creations"  # 替换 {your_id} 为实际的任务 ID
headers = {
    "Authorization": f"Token {api_key}"  # 替换 {your_api_key} 为您的实际 API Key
}

# 发送 GET 请求
response = requests.get(api_url, headers=headers)

# 打印响应内容
print("Response Status Code:", response.status_code)
if response.status_code == 200:
    print("Response Content:", response.json())
else:
    print("Error:", response.text)