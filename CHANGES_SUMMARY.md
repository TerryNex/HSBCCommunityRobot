# 改進總結 (Changes Summary)

本次更新實現了以下四個主要改進：

## 1. 顯示用戶名 (Username Display)

### 變更文件：
- `forum_client.py`: 在 `get_conversations()` 方法中添加 `username` 字段提取
- `.github/workflows/list-recent-subjects.yml`: 添加用戶名顯示
- `main.py`: 在日誌中顯示標題、用戶名和消息

### 實現細節：
```python
# forum_client.py - 從 API 響應中提取用戶名
"username": item.get("ParticipantDisplayName", "") or item.get("CreatedByName", "Unknown")
```

現在兩個工作流都會顯示：
- 帖子標題 (Title)
- 用戶名 (Username)  
- 消息內容 (Message)

## 2. Git-based 存儲替代 SQLite 數據庫

### 變更文件：
- **新增**: `git_storage.py` - 基於 JSON 文件的存儲模塊
- `main.py`: 使用 `GitStorage` 替代 `DatabaseManager`
- `.github/workflows/run-reply-bot.yml`: 
  - 更新權限為 `contents: write`
  - 添加自動提交和推送 `replied_posts.json` 的步驟

### 實現細節：
```python
# git_storage.py - 新的存儲類
class GitStorage:
    """使用 JSON 文件存儲已回復的帖子 ID"""
    - 將數據保存到 replied_posts.json
    - 每次標記回復時自動保存
    - 格式: {"post_id": "timestamp"}
```

### 工作流程：
1. Checkout 代碼倉庫
2. 運行 bot (讀取/更新 replied_posts.json)
3. Git commit 和 push 更改（如果有）

### 優點：
- ✅ 永久存儲（不受 artifact 90天限制）
- ✅ 版本控制和歷史追蹤
- ✅ 透明度高，可直接查看 JSON 文件
- ✅ 不需要外部數據庫

## 3. 改進 AI Prompt - 結合標題和內容

### 變更文件：
- `ai_handler.py`: 更新 `generate_reply()` 接受標題和內容兩個參數
- `main.py`: 傳遞標題給 AI handler
- `tests/test_api_steps.py`: 更新測試以匹配新的函數簽名

### 改進的 System Prompt：
```python
system_prompt = (
    ...
    "6. **重要**: 如果帖子內容很簡短（如 'pls adv'、'too bad'），"
    "你必須結合帖子標題來理解用戶真正想問什麼或討論什麼，然後給出有意義的回覆。\n"
    "7. 'pls adv' 通常是請求建議的意思，請根據標題內容給出實質性的建議或看法。\n"
    "8. 回覆時使用 <br> 標籤來換行，而不是使用普通的換行符。"
)
```

### 用戶消息構造：
```python
if post_title and post_title.strip():
    user_message = f"帖子標題：{post_title}\n帖子內容：{post_content}\n\n請生成回覆："
else:
    user_message = f"帖子內容：{post_content}\n\n請生成回覆："
```

### 效果：
- 對於簡短內容如 "pls adv"，AI 會根據標題理解真實意圖
- 避免生成無意義的回復（如 "ADV是什麼意思"）
- 生成更有價值的討論內容

## 4. 使用 `<br>` 標籤換行

### 變更文件：
- `ai_handler.py`: 在返回回復前將 `\n` 轉換為 `<br>`

### 實現：
```python
# Convert regular newlines to <br> tags for forum formatting
reply = reply.replace('\n', '<br>')
```

這符合論壇的 HTML 格式要求，確保換行正確顯示。

## 測試和驗證

### 語法檢查：
```bash
python3 -m py_compile main.py ai_handler.py forum_client.py git_storage.py
```
✅ 所有文件編譯成功

### 模塊導入：
```bash
python3 -c "import main; import ai_handler; import forum_client; import git_storage; ..."
```
✅ 所有模塊導入成功

### 更新的測試：
- `test_perplexity_api`: 現在測試帶標題的 AI 回復生成

## 向後兼容性

- `ai_handler.generate_reply()` 的 `post_title` 參數是可選的（默認為空字符串）
- 如果沒有標題，仍然可以正常工作
- 舊的 `replied_posts.db` 文件會被忽略（已在 .gitignore 中）

## 文件變更概覽

```
修改的文件：
  .github/workflows/list-recent-subjects.yml  - 添加用戶名顯示
  .github/workflows/run-reply-bot.yml         - Git 存儲集成
  ai_handler.py                                - 改進 prompt，<br> 標籤
  forum_client.py                              - 提取用戶名
  main.py                                      - 使用 GitStorage，傳遞標題
  tests/test_api_steps.py                      - 更新測試

新增文件：
  git_storage.py                               - Git-based 存儲模塊
```

## 下一步

1. 運行 `list-recent-subjects` 工作流測試用戶名顯示
2. 運行 `run-reply-bot` 工作流測試所有改進功能
3. 檢查 `replied_posts.json` 是否自動提交到倉庫
4. 驗證 AI 回復質量是否提升

## 注意事項

- 確保 GitHub Actions 有 `contents: write` 權限
- `replied_posts.json` 會自動創建和管理，不需要手動編輯
- 提交消息包含 `[skip ci]` 以避免觸發無限循環
