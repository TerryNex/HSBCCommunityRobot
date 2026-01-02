# Copilot Instructions for HSBCCommunityRobot

## Project Overview

**Forum Reply Automator (FRA)** is a Python-based automated forum reply tool designed to simulate human behavior and use AI to generate high-quality reply content for the HSBC Community forum (Square Community platform).

### Repository Statistics
- **Language**: Python 3.12.3
- **Size**: Small (~10 Python files)
- **Project Type**: Web automation script with AI integration
- **External APIs**: Perplexity AI API, Square Community API
- **Database**: SQLite (replied_posts.db)

### Key Technologies
- **HTTP Client**: requests library with session management
- **Environment Management**: python-dotenv for configuration
- **AI Integration**: Perplexity AI API for content generation
- **Testing Framework**: pytest
- **Database**: SQLite3 (built-in)

## Dependencies and Setup

### Required Dependencies
**ALWAYS** install these dependencies before running any code:
```bash
pip install requests python-dotenv
```

For testing, also install:
```bash
pip install pytest
```

### Installed Package Versions (verified working)
- requests==2.31.0
- python-dotenv==1.2.1
- pytest==9.0.2

### Environment Configuration
The application requires a `.env` file in the root directory. **NEVER commit .env files**.

To set up:
1. Copy `.env.example` to `.env`
2. Fill in required values:
   - `AI_API_KEY`: Perplexity AI API key
   - `AI_MODEL`: AI model name (default: "sonar")
   - `FORUM_BASE_URL`: Forum base URL
   - `FORUM_USERNAME`: Forum login username
   - `FORUM_PASSWORD`: Forum login password
   - `CHECK_INTERVAL_SECONDS`: Check interval (default: 3600)
   - `RANDOM_DELAY_RANGE`: Maximum random delay in seconds (default: 300)

**Note**: Tests and main.py will run with None values if .env is missing, but API calls will fail.

## Build and Validation Commands

### Syntax Checking
To verify Python syntax without executing:
```bash
python3 -m py_compile main.py ai_handler.py forum_client.py db_manager.py config_manager.py utils.py
```
This should output nothing if successful, or syntax errors if there are issues.

### Module Import Testing
To verify all modules can be imported:
```bash
python3 -c "import main; import ai_handler; import forum_client; import db_manager; import config_manager; import utils; print('All modules imported successfully')"
```

### Running Tests
**ALWAYS** run tests from the repository root:
```bash
python3 -m pytest tests/ -v
```

To run a specific test:
```bash
python3 -m pytest tests/test_api_steps.py::test_perplexity_api -v
```

To collect tests without running:
```bash
python3 -m pytest --collect-only tests/
```

**Important**: Some tests require valid API credentials in .env file and may make real API calls. Tests may take 10-30 seconds to complete due to network requests.

### Running the Application
To run the main automation script:
```bash
python3 main.py
```

**Warning**: This will make real API calls to the forum and AI service if credentials are configured. The script may run for extended periods (several minutes) as it processes posts.

## Project Architecture

### Root Directory Structure
```
/
├── .env.example          # Environment variable template
├── .gitignore           # Git ignore rules
├── README.md            # Project documentation (in Chinese)
├── agent.md             # Agent work log (historical)
├── config.json          # Stores auth token (generated at runtime)
├── replied_posts.db     # SQLite database tracking replied posts
├── main.py              # Entry point - orchestrates all components
├── ai_handler.py        # AI reply generation via Perplexity API
├── forum_client.py      # HTTP client for Square Community API
├── db_manager.py        # SQLite database operations
├── config_manager.py    # JSON config file management
├── utils.py             # Utility functions (delays, headers, logging)
├── test.py              # Standalone test script (legacy)
└── tests/
    └── test_api_steps.py # Pytest test suite (7 tests)
```

### Module Responsibilities

**main.py** (Entry Point)
- Coordinates all components
- Implements 6-step forum interaction logic:
  1. Validate session token
  2. Login if expired
  3. Get page info (target: '傾下講下')
  4. Get room info (priority: "Recent Subjects")
  5. Get conversations in rooms
  6. Generate AI reply and submit with like
- Handles de-duplication via database
- Implements human-like delays between actions

**forum_client.py** (API Client)
- `ForumClient` class manages all HTTP interactions
- Uses `requests.Session` for persistent connections and header management
- Base URLs:
  - Query API: https://serviceapi-query.square-community.com.au
  - Command API: https://serviceapi-command.square-community.com.au
  - Origin: https://hsbccommunityhk.square-community.com.au
- Key methods:
  - `validate_session()`: Check if auth token is valid
  - `login()`: Get new auth token (returns plain text token)
  - `get_page_info()`: Get page GUID for target forum section
  - `get_room_info()`: Get list of rooms in page
  - `get_conversations()`: Get posts in a room
  - `reply_and_like()`: Submit reply (multipart/form-data) and like
- **Critical**: Uses `files` parameter for reply submission, not `data` or `json`

**ai_handler.py** (AI Integration)
- `AIHandler` class for Perplexity AI integration
- Generates human-like forum replies in Chinese
- System prompt optimized to avoid AI-like language
- Post-processes responses to remove citation markers
- Uses temperature=0.7, top_p=0.9 for natural variation

**db_manager.py** (Database)
- `DatabaseManager` class for SQLite operations
- Schema: `replied_posts(post_id TEXT PRIMARY KEY, replied_at TIMESTAMP)`
- Methods:
  - `is_replied(post_id)`: Check if post was already replied to
  - `mark_as_replied(post_id)`: Record post as replied
- Auto-creates database and table if not exists

**config_manager.py** (Configuration)
- `ConfigManager` class for persistent JSON config
- Stores auth token in config.json
- Auto-creates config.json if not exists

**utils.py** (Utilities)
- Logging configuration (DEBUG level by default)
- `get_random_headers()`: Returns random User-Agent
- `human_delay(max_seconds)`: Random delay 5 to max_seconds
- Exports `logger` for consistent logging across modules

### Configuration Files

**config.json** (Auto-generated)
- Stores authentication token from login
- Created/updated by `config_manager.py`
- **Do not manually edit** - managed by application

**replied_posts.db** (Auto-generated)
- SQLite database tracking replied posts
- Created by `db_manager.py` on first run

**.gitignore**
- Excludes: logs, temp files, .env files, IDE files, __pycache__, venv
- **Important**: Excludes .env but NOT config.json or replied_posts.db

## Testing

### Test Structure
The test suite in `tests/test_api_steps.py` has 7 tests covering:
1. `test_perplexity_api`: AI reply generation
2. `test_step1_validate_session`: Token validation
3. `test_step2_login`: Login and token refresh
4. `test_step3_get_page_guid`: Page info retrieval
5. `test_step4_get_room_guid`: Room info retrieval
6. `test_step5_get_conversation_id`: Conversation retrieval
7. `test_step6_reply_and_like`: Reply and like submission

**Note**: Tests use pytest fixtures for `forum_client` and `ai_handler`.

### Running Tests Successfully
Tests require valid .env configuration and make real API calls. If you modify code:

1. **Verify syntax first**:
   ```bash
   python3 -m py_compile <modified_file>.py
   ```

2. **Test module import**:
   ```bash
   python3 -c "import <modified_module>"
   ```

3. **Run specific test** (if relevant):
   ```bash
   python3 -m pytest tests/test_api_steps.py::<test_name> -v
   ```

4. **Run full test suite** (may take 30+ seconds):
   ```bash
   python3 -m pytest tests/ -v
   ```

## Common Issues and Workarounds

### Issue: ModuleNotFoundError for requests or dotenv
**Solution**: Install dependencies first:
```bash
pip install requests python-dotenv
```

### Issue: Tests hang or timeout
**Cause**: Network requests to real APIs can be slow
**Solution**: This is expected behavior. Wait 10-30 seconds. If >60 seconds, check network/API status.

### Issue: "Error: AI_API_KEY is missing" in logs
**Cause**: .env file not configured or missing AI_API_KEY
**Solution**: Create .env from .env.example and add valid API key

### Issue: Login fails (401/403 errors)
**Cause**: Invalid credentials or expired session
**Solution**: Check FORUM_USERNAME and FORUM_PASSWORD in .env

### Issue: "Bufound page" typo in logs
**Cause**: Typo in forum_client.py line 109 ("Bufound" should be "Found")
**Note**: This is a known cosmetic issue and does not affect functionality

### Issue: Database locked errors
**Cause**: Multiple instances accessing replied_posts.db simultaneously
**Solution**: Ensure only one instance of main.py runs at a time

## Code Conventions and Best Practices

### Python Style
- Uses standard Python naming conventions (snake_case for functions/variables)
- Classes use PascalCase (e.g., `ForumClient`, `AIHandler`)
- Minimal comments - code is mostly self-documenting
- Uses f-strings for string formatting
- Imports grouped: stdlib, third-party, local

### HTTP Request Patterns
When modifying `forum_client.py`, **always**:
1. Use `self.session.post()` or `self.session.get()`, never `requests.post()` directly
2. For reply submission, use `files` parameter with tuple format: `(None, json_string)`
3. Include `response.raise_for_status()` for error handling
4. Headers are managed in session - avoid manual header construction

### Error Handling
- Uses try/except blocks for network operations
- Logs errors with `logger.error()`
- Returns `None` or `False` on failure, not raising exceptions
- Uses `response.raise_for_status()` for HTTP error detection

### Logging
- Uses Python `logging` module configured in `utils.py`
- Default level: DEBUG
- Format: `%(asctime)s - %(levelname)s - %(message)s`
- Log messages in Chinese for user-facing events
- Use `logger.info()` for normal flow, `logger.error()` for failures

## Security Considerations

### Credentials
- **Never hardcode** API keys, passwords, or tokens in source code
- Always use .env for sensitive configuration
- config.json contains auth token - avoid committing if contains real credentials
- .gitignore properly excludes .env files

### API Usage
- Uses Bearer token authentication for forum API
- Tokens stored in config.json and session headers
- Login returns plain text token, not JSON
- No explicit logout mechanism - tokens may have server-side expiration

## Validation Steps

Before committing changes:

1. **Syntax check all modified Python files**:
   ```bash
   python3 -m py_compile <file1>.py <file2>.py
   ```

2. **Test module imports**:
   ```bash
   python3 -c "import <module1>; import <module2>"
   ```

3. **Run relevant tests** (if .env configured):
   ```bash
   python3 -m pytest tests/ -v
   ```

4. **Check for common issues**:
   - Verify no hardcoded credentials
   - Ensure proper error handling in HTTP requests
   - Check that session is used instead of direct requests calls
   - Validate Chinese character encoding (use `ensure_ascii=False`)

## Important Notes for Agents

### DO Always:
- Install dependencies before running any code or tests
- Use `python3 -m pytest` (not just `pytest`) for consistency
- Check if .env exists before expecting tests to pass fully
- Use session-based HTTP requests in forum_client.py
- Include proper error handling with raise_for_status()
- Test syntax before running full tests
- Trust that this instructions file is accurate - only search if information seems incomplete

### DO NOT:
- Commit .env files with credentials
- Use `requests.post()` directly - always use `self.session.post()`
- Expect fast test execution - API calls take time
- Run multiple instances of main.py simultaneously
- Use `data` or `json` parameter for reply submission - use `files` parameter
- Remove or modify existing error handling without replacement
- Change the database schema without updating db_manager.py

### When Making Changes:
1. Understand the 6-step forum interaction flow before modifying main.py or forum_client.py
2. Maintain the multipart/form-data format for replies (files parameter)
3. Keep session-based request pattern
4. Preserve Chinese language support in AI prompts and logging
5. Test incrementally: syntax → import → unit test → full test
6. Consider that tests make real API calls - don't over-test during development

This file should provide everything needed to work efficiently with this codebase. If you encounter issues not documented here, investigate and consider updating these instructions for future reference.
