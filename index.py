from flask import Flask, request, jsonify
import datetime
import requests

app = Flask(__name__)

# ======================= 【我已经帮你填好！】=======================
DING_APPKEY = "dingnluxfh3ujsfgcvuk"
DING_APPSECRET = "3EcLobfzjCONWs8EYVZeYaQPe25u1Hx0otrmLdkns4h5Lf4ReRNqJPpydvkFB18_"
DING_AGENTID = 4454798497
# ==================================================================

VOLC_API = "https://qingtian.dingtalk.com/api/proxy/v1/chat"
VOLC_APPID = "d7auhllfpps169gd780"
VOLC_KEY = "d7bgk5plfpps169gd780"

# 钉钉校验必须走这个 GET/HEAD 接口
@app.route('/', methods=['GET', 'HEAD'])
def health_check():
    return jsonify({
        "code": 200,
        "status": "ok",
        "msg": "服务运行正常"
    }), 200

# 处理钉钉消息
@app.route('/', methods=['POST'])
def handle_message():
    try:
        data = request.get_json()
        if not data:
            return "ok", 200

        user_id = data.get("senderId")
        question = data.get("text", {}).get("content", "").strip()

        if not user_id or not question:
            return "ok", 200

        # 调用火山AI（自动带 Date 头）
        date_str = datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")
        headers = {
            "Content-Type": "application/json",
            "AppId": VOLC_APPID,
            "Authorization": f"Bearer {VOLC_KEY}",
            "Date": date_str
        }

        resp = requests.post(
            "https://qingtian.dingtalk.com/api/proxy/v1/chat",
            json={"query": question, "userId": user_id},
            headers=headers,
            timeout=10
        )

        answer = resp.json().get("answer", "我收到你的消息啦！")

        # 发回钉钉
        token_resp = requests.get(
            f"https://oapi.dingtalk.com/gettoken?appkey={DING_APPKEY}&appsecret={DING_APPSECRET}",
            timeout=5
        )
        access_token = token_resp.json().get("access_token")

        if access_token:
            requests.post(
                f"https://oapi.dingtalk.com/topapi/message/corpconversation/asyncsend_v2?access_token={access_token}",
                json={
                    "agent_id": DING_AGENTID,
                    "userid_list": user_id,
                    "msg": {
                        "msgtype": "text",
                        "text": {"content": answer}
                    }
                },
                timeout=8
            )

    except Exception as e:
        print("error", str(e))

    return "ok", 200

if __name__ == '__main__':
    app.run()
