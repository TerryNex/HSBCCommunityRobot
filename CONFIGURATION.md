# Configuration Guide

This document explains the environment variables and GitHub Actions workflows for the Forum Reply Automator.

## Environment Variables

### Required Variables

These variables must be set in your `.env` file (local) or as GitHub Repository Variables (GitHub Actions):

- `FORUM_BASE_URL` - Base URL of the forum
- `FORUM_USERNAME` - Your forum username
- `FORUM_PASSWORD` - Your forum password
- `AI_API_KEY` - API key for AI service
- `AI_MODEL` - AI model to use (e.g., `gemini-1.5-flash`)

### Optional Variables

- `ROOM_TITLES` (default: `"Recent Subjects"`)
  - Comma-separated list of room titles to process
  - Example: `"Recent Subjects,精明消費,理財有道,其他"`
  - Whitespace around each title is automatically trimmed
  - Empty or whitespace-only values will use the default

- `CONVERSATION_LIMIT` (default: `5`)
  - Number of conversations to fetch per room
  - Must be a valid integer greater than or equal to 1
  - Falls back to `5` if invalid, missing, or less than 1

- `RANDOM_DELAY_RANGE` (default: `300`)
  - Maximum random delay in seconds for human-like behavior

## Local Development

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and fill in your values:
   ```env
   FORUM_BASE_URL=https://example-forum.com
   FORUM_USERNAME=your_username
   FORUM_PASSWORD=your_password
   AI_API_KEY=your_api_key
   AI_MODEL=gemini-1.5-flash
   ROOM_TITLES=Recent Subjects,精明消費,理財有道
   CONVERSATION_LIMIT=10
   ```

3. Run the script:
   ```bash
   python main.py
   ```

## GitHub Actions Workflows

### Setup

1. Go to your repository Settings → Secrets and variables → Actions

2. Add the following **Variables** (all configuration is stored as plaintext variables):
   - `FORUM_BASE_URL`
   - `FORUM_USERNAME`
   - `FORUM_PASSWORD`
   - `AI_API_KEY`
   - `AI_MODEL`
   - `ROOM_TITLES` (e.g., `Recent Subjects,精明消費,理財有道`)
   - `CONVERSATION_LIMIT` (optional, defaults to workflow-specific values)
   - `RANDOM_DELAY_RANGE` (optional, defaults to 300)

**Note:** All values are stored as Repository Variables rather than Secrets, as encryption is not required for this use case.

### Workflow 1: List Recent Subjects (Read-Only)

**File:** `.github/workflows/list-recent-subjects.yml`

**Purpose:** Fetch and display recent conversations without replying.

**Trigger:** Manual (`workflow_dispatch`)

**Behavior:**
- Fetches the latest 30 conversations from allowed rooms
- Displays title and message preview for each conversation
- Does not reply to any posts
- Useful for manual review before running the reply bot

**How to run:**
1. Go to Actions tab in GitHub
2. Select "List Recent Subjects" workflow
3. Click "Run workflow"
4. Check the logs to see the list of recent conversations

### Workflow 2: Daily Reply Bot (Automated)

**File:** `.github/workflows/daily-reply.yml`

**Purpose:** Automated daily reply bot that runs at a fixed time.

**Trigger:** 
- Scheduled: Daily at 10:00 Hong Kong Time (02:00 UTC)
- Manual: `workflow_dispatch`

**Fixed Parameters:**
- `CONVERSATION_LIMIT`: 15 conversations
- `HOURS_FILTER`: 21 hours (replies to posts from the last 21 hours)

**Behavior:**
- Runs automatically every day at 10:00 HKT
- Fetches conversations from allowed rooms
- Filters posts older than 21 hours
- Filters out already-replied posts (using replied_posts.json)
- Generates AI replies for up to 15 conversations
- Posts replies and likes them
- Commits and pushes updated replied_posts.json to repository

**How to manually trigger:**
1. Go to Actions tab in GitHub
2. Select "Daily Reply Bot" workflow
3. Click "Run workflow"
4. Check the logs to see the bot's activity

### Workflow 3: Run Reply Bot (Manual)

**File:** `.github/workflows/run-reply-bot.yml`

**Purpose:** Run the full reply bot with configurable conversation limit.

**Trigger:** Manual (`workflow_dispatch`)

**Inputs:**
- `conversation_limit_choice`: Choose from `5`, `10`, `15`, or `custom`
- `conversation_limit_custom`: Specify a custom number (used only when choice is `custom`)

**Behavior:**
- Downloads previous replied posts database (if exists)
- Determines final conversation limit based on inputs
- Runs the full bot logic:
  - Fetches conversations from allowed rooms
  - Filters out already-replied posts
  - Generates AI replies
  - Posts replies and likes them
  - Updates the replied posts database
- Uploads updated database for next run

**How to run:**
1. Go to Actions tab in GitHub
2. Select "Run Reply Bot" workflow
3. Click "Run workflow"
4. Choose conversation limit (5, 10, 15, or custom)
5. If custom, enter the number in the custom field
6. Click "Run workflow"
7. Check the logs to see the bot's activity

### Database Persistence in GitHub Actions

The reply bot workflow uses GitHub Actions artifacts to persist the `replied_posts.db` database between runs:

1. Before running, it downloads the previous database artifact
2. After running, it uploads the updated database
3. This prevents the bot from replying to the same posts multiple times

**Note:** Artifacts are retained for 90 days by default.

## Avoiding Duplicate Replies

The bot uses a SQLite database (`replied_posts.db`) to track which posts have been replied to:

- **Local development:** Database file is created in the project directory
- **GitHub Actions:** Database is persisted as a workflow artifact

The database is automatically created if it doesn't exist. Each successful reply is recorded with:
- `post_id`: Unique identifier of the post
- `replied_at`: Timestamp when the reply was posted

Before replying, the bot checks if a post has already been replied to and skips it if so.

## Troubleshooting

### Environment variables not working

- **Local:** Make sure `.env` file exists and `python-dotenv` is installed
- **GitHub Actions:** Verify variables/secrets are set in repository settings

### Invalid CONVERSATION_LIMIT

If the value is not a valid integer, the bot will:
1. Log a warning
2. Fall back to the default value of `5`

### Database issues in GitHub Actions

If the database artifact is missing or corrupted:
1. The bot will create a new database
2. This may cause it to reply to previously replied posts
3. To prevent this, ensure artifacts are not deleted prematurely

### Room filtering not working

Check that:
1. `ROOM_TITLES` is properly formatted (comma-separated)
2. Room titles match exactly (case-sensitive)
3. No extra whitespace (though the code trims it automatically)
