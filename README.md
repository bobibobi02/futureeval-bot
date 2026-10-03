# FutureEval Fall 2026 bot (Metaculus)

Runs the official template forecasting bot on GitHub Actions every 30 minutes.
It needs ONE secret: `METACULUS_TOKEN` (the bot's access token from your Metaculus bot settings page).
LLM costs are covered by Metaculus for the seasonal tournament.

## Setup
1. Repo Settings > Secrets and variables > Actions > New repository secret.
   Name: `METACULUS_TOKEN`. Value: your bot token. Never commit the token to a file.
2. Actions tab > enable workflows > "Forecast on FutureEval tournament" > Run workflow.
3. Open the run log. It should list questions and published forecasts. After that it repeats on its own.

## Optional
- `OPENROUTER_API_KEY`, `ASKNEWS_SECRET`: extra secrets the template picks up automatically.
- `BOT_DEFAULT_MODEL`, `BOT_RESEARCH_MODEL`, `BOT_PREDICTIONS`: see main.py.
- Dry run locally: `python main.py --mode test_questions --dry-run`
