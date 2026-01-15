import json
import os

import requests
from dotenv import load_dotenv

load_dotenv()

class AIHandler:
    def __init__(self):
        self.api_key = os.getenv("AI_API_KEY")
        self.model = os.getenv("AI_MODEL", "sonar")
        self.url = "https://api.perplexity.ai/chat/completions"

    def generate_reply(self, post_content, post_title=""):
        """
        Generates a human-like reply using Perplexity API.
        Optimized for forum interaction and anti-detection.
        
        Args:
            post_content: The main content/message of the post
            post_title: The title of the post (optional but recommended)
        """
        if not self.api_key:
            return "Error: AI_API_KEY is missing."

        system_prompt = (
            "你係一個住喺香港嘅普通用戶，活躍於本地討論區。你嘅目標係根據帖子內容俾回覆，或者引起討論。\n"
            "規則：\n"
            "1. 語氣自然、口語化，用常見嘅討論區俚語或語句（如：推、真的、同意、正、抵）。唔好提及『原PO』等稱呼，直接針對內容回覆。\n"
            "2. 你本身就住喺香港，回覆時要好似一般香港街坊咁自然傾計。絕對唔好出現『香港那邊』、『你們香港』、『你們那裡』、『在香港那邊』等好似局外人嘅表達方式。\n"
            "3. 避免使用『身為一個 AI』、『以下是我的建議』、『根據搜尋結果』等 AI 特徵明確嘅語句。除非用戶直接問你係咪 AI，否則唔好透露。\n"
            "4. 回覆唔好太長，通常 1-2 句就夠，除非原帖需要詳細討論。\n"
            "5. 有時候可以帶一啲主觀情緒，但保持禮貌友善。\n"
            "6. 唔好用太完美嘅排版或者條列式回覆。標點符號隨意啲，句子結尾可以唔使句號，偶爾用換行代替逗號。\n"
            "7. **重要**: 如果帖子內容好短（如 'pls adv'、'too bad'），你要結合帖子標題嚟理解用戶想問乜或者討論乜，然後俾有意義嘅回覆。\n"
            "8. 'pls adv' 通常係請求建議嘅意思，請根據標題內容俾實質性嘅建議或睇法。\n"
            "9. 回覆時用 <br> 標籤嚟換行，而唔係用普通嘅換行符。\n"
            "10. 可以用繁體中文書面語或者廣東話口語，視乎帖子嘅風格同語氣嚟配合。"
        )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Construct user message with both title and content
        if post_title and post_title.strip():
            user_message = f"帖子標題：{post_title}\n帖子內容：{post_content}\n\n請生成回覆："
        else:
            user_message = f"帖子內容：{post_content}\n\n請生成回覆："

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            "max_tokens": 200,
            "temperature": 0.7,
            "top_p": 0.9,
            "stream": False
        }

        try:
            response = requests.post(self.url, json=payload, headers=headers)
            if response.status_code != 200:
                print(f"Perplexity API Error: {response.status_code} - {response.text}")
            response.raise_for_status()
            data = response.json()
            reply = data['choices'][0]['message']['content'].strip()

            # Post-processing: Remove [1], [2] citation markers
            import re
            reply = re.sub(r'\[\d+\]', '', reply)

            # Remove any potential "Reply:" prefix if AI generates it
            if reply.startswith("回覆："):
                reply = reply.replace("回覆：", "", 1).strip()
            
            # Convert regular newlines to <br> tags for forum formatting
            reply = reply.replace('\n', '<br>')
            
            return reply
        except Exception as e:
            print(f"Exception during Perplexity reply generation: {e}")
            return None
