# Forum Reply Automator (FRA)

FRA 是一個基於 Python 的自動化討論區回帖工具，旨在模擬真人行為並利用 AI 生成高質量的回帖內容。

## 發展目標

- **自動化**：每天定時於香港時間 10:00 自動抓取帖子並回覆。
- **抗檢測**：通過隨機延遲、模擬 User-Agent、AI 提示工程（Prompt Engineering）等手段，避免被識別為機器人。
- **去重**：使用 JSON 文件記錄已回覆的帖子 ID。

## 主要模組

- `main.py`: 腳本入口，負責協調各個組件。
- `ai_handler.py`: 調用 AI API 並生成擬人化的回答。
- `forum_client.py`: 負責與目標討論區進行網絡交互（抓取與發帖）。
- `db_manager.py`: 管理 SQLite 資料庫。
- `utils.py`: 提供隨機延遲、Header 生成等工具函數。

## 部署指南

### 本地運行

1. **安裝環境**:

   ```bash
   pip install requests python-dotenv
   ```

2. **配置變數**:
   在根目錄創建 `.env` 文件，填入 AI API Key 和目標論壇配置。

3. **手動運行**:
   ```bash
   python3 main.py
   ```

### GitHub Actions 自動化部署

本項目已配置 GitHub Actions 工作流，實現每日自動回帖：

- **Daily Reply Bot**：每天香港時間 10:00 自動運行
  - 自動處理 15 個對話
  - 回覆最近 21 小時內的帖子
  - 自動提交已回覆記錄

詳細配置請參考 [CONFIGURATION.md](CONFIGURATION.md)。

## 注意事項

- 本工具僅供學術研究與技術開發參考，請遵守各討論區的使用協議（Terms of Service）。
