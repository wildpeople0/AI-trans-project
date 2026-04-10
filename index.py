from flask import Flask, request, jsonify
import json
import datetime
import requests

app = Flask(__name__)

# ========== 你只需要改这3个钉钉信息 ==========
DING_APPKEY = "dingnluxfh3ujsfgcvuk"
DING_APPSECRET = "3EcLobfzjCONWs8EYVZeYaQPe25u1Hx0otrmLdkns4h5Lf4ReRNqJPpydvkFB18_"
DING_AGENTID = 4454798497  # 纯数字，不要引号
# ==============================================

VOLC_API = "https://qingtian.dfmc.com.cn/api/proxy/api/v1"
VOLC_APPID = "d7auhl1lfpps169gd780"
VOLC_KEY = "d7bgk5plfpps169gffs0"

# 获取钉钉token
def get_dingtalk_token():
    url = f"https://oapi.dingtalk.com/gettoken?appkey={DING_APPKEY}&appsecret={DING_APPSECRET}"
    return requests.get(url).json().get("access_token")

# 发消息回钉钉
def send_dingtalk_msg(user_id, content):
    token = get_dingtalk_token()
    url = f"https://oapi.dingtalk.com/topapi/message/corpconversation/asyncsend_v2?access_token={token}"
    body = {
        "agent_id": DING_AGENTID,
        "userid_list": user_id,
        "msg": {"msgtype": "text", "text": {"content": content}}
    }
    requests.post(url, json=body)

# 处理钉钉消息
@app.route('/', methods=['POST'])
def index():
    data = request.get_json()
    user_id = data.get("senderId")
    question = data.get("text", {}).get("content", "").strip()

    if not user_id or not question:
        return "ok"

    # 调用火山AI，补齐Date头
    date = datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")
    headers = {
        "Content-Type": "application/json",
        "AppId": VOLC_APPID,
        "Authorization": "Bearer " + VOLC_KEY,
        "Date": date
    }
    resp = requests.post(VOLC_API, json={"query": question, "userId": user_id}, headers=headers)
    answer = resp.json().get("answer", "抱歉，我暂时无法回答~")
    send_dingtalk_msg(user_id, answer)
    return "ok"

# 处理浏览器GET访问
@app.route('/', methods=['GET'])
def get():
    return jsonify({"msg": "钉钉机器人中转服务运行正常"})

if __name__ == '__main__':
    app.run()