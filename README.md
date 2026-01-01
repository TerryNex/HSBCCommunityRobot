# Forum Reply Automator (FRA)

FRA 是一個基於 Python 的自動化討論區回帖工具，旨在模擬真人行為並利用 AI 生成高質量的回帖內容。

## 發展目標

- **自動化**：定時抓取帖子並回覆。
- **抗檢測**：通過隨機延遲、模擬 User-Agent、AI 提示工程（Prompt Engineering）等手段，避免被識別為機器人。
- **去重**：使用 SQLite 記錄已回覆的帖子 ID。

## 主要模組

- `main.py`: 腳本入口，負責協調各個組件。
- `ai_handler.py`: 調用 AI API 並生成擬人化的回答。
- `forum_client.py`: 負責與目標討論區進行網絡交互（抓取與發帖）。
- `db_manager.py`: 管理 SQLite 資料庫。
- `utils.py`: 提供隨機延遲、Header 生成等工具函數。

## 部署指南

1. **安裝環境**:

   ```bash
   pip install requests python-dotenv
   ```

2. **配置變數**:
   在根目錄創建 `.env` 文件，填入 AI API Key 和目標論壇配置。
3. **定時任務 (Linux)**:
   使用 `crontab -e` 設置每小時執行一次：

   ```bash
   0 * * * * python3 /path/to/project/main.py >> /path/to/project/cron.log 2>&1
   ```

## 注意事項

- 本工具僅供學術研究與技術開發參考，請遵守各討論區的使用協議（Terms of Service）。
