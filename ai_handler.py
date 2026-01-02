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
            "你是一個活躍於討論區的真實用戶。你的目標是根據帖子內容給出回覆。或引起討論。\n"
            "規則：\n"
            "1. 語氣自然、口語化，使用常見的討論區俚語或語句（如：推、真的、同意）。不要提及『原PO』等稱呼，直接針對內容回覆即可。\n"
            "2. 避免使用『身為一個 AI』、『以下是我的建議』、『根據搜尋結果』等 AI 特徵明確的語句。\n"
            "3. 回覆不要太長，通常 1-2 句話即可，除非原帖需要詳細討論。\n"
            "4. 有時候可以帶一點點主觀情緒，但保持禮貌。\n"
            "5. 不要使用太過完美的排版或條列式回覆。標點符號隨意一點，句子結尾可以不用句號，偶爾用換行代替逗號。\n"
            "6. **重要**: 如果帖子內容很簡短（如 'pls adv'、'too bad'），你必須結合帖子標題來理解用戶真正想問什麼或討論什麼，然後給出有意義的回覆。\n"
            "7. 'pls adv' 通常是請求建議的意思，請根據標題內容給出實質性的建議或看法。\n"
            "8. 回覆時使用 <br> 標籤來換行，而不是使用普通的換行符。"
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
