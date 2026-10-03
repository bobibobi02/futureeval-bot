"""
Forecasting bot for the Metaculus FutureEval (Fall 2026) AI benchmark.

Built on the official template bot shipped in the `forecasting-tools` package
(FallTemplateBot2026). It works with ONLY a METACULUS_TOKEN secret: the template
then uses the free Metaculus LLM proxy ("metaculus/..." models).
Optional secrets (OPENROUTER_API_KEY, ASKNEWS_SECRET, ...) are picked up
automatically by the template defaults.

Optional env overrides (no code change needed):
  BOT_DEFAULT_MODEL   e.g. "metaculus/gpt-4o" or "openrouter/anthropic/claude-sonnet-4"
  BOT_RESEARCH_MODEL  e.g. "asknews/news-summaries" or "metaculus/gpt-4o-search-preview"
  BOT_PREDICTIONS     number of forecasts averaged per question (default 5)

Run:  python main.py --mode tournament | metaculus_cup | test_questions
"""
import argparse
import asyncio
import logging
import os

from forecasting_tools import GeneralLlm, MetaculusClient
from forecasting_tools.forecast_bots.official_bots.template_bot_2026_fall import (
    FallTemplateBot2026,
)

logger = logging.getLogger("my_bot")


def build_llms() -> dict | None:
    """Return an llms dict only if the user overrode models via env vars."""
    llms: dict = {}
    default_model = os.getenv("BOT_DEFAULT_MODEL", "").strip()
    research_model = os.getenv("BOT_RESEARCH_MODEL", "").strip()
    if default_model:
        llms["default"] = GeneralLlm(
            model=default_model, temperature=0.3, timeout=120, allowed_tries=2
        )
    if research_model:
        llms["researcher"] = (
            research_model
            if research_model.startswith("asknews/")
            else GeneralLlm(model=research_model, temperature=0.1)
        )
    return llms or None


def build_bot(publish: bool = True) -> FallTemplateBot2026:
    return FallTemplateBot2026(
        research_reports_per_question=1,
        predictions_per_research_report=int(os.getenv("BOT_PREDICTIONS", "5")),
        use_research_summary_to_forecast=False,
        publish_reports_to_metaculus=publish,
        folder_to_save_reports_to=None,
        skip_previously_forecasted_questions=True,
        extra_metadata_in_explanation=True,
        llms=build_llms(),
    )


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    lite = logging.getLogger("LiteLLM")
    lite.setLevel(logging.WARNING)
    lite.propagate = False

    parser = argparse.ArgumentParser(description="FutureEval Fall 2026 bot")
    parser.add_argument(
        "--mode",
        choices=["tournament", "metaculus_cup", "test_questions"],
        default="tournament",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="forecast but do NOT publish anything to Metaculus",
    )
    args = parser.parse_args()

    bot = build_bot(publish=not args.dry_run)
    client = MetaculusClient()

    if args.mode == "tournament":
        reports = asyncio.run(
            bot.forecast_on_tournament(
                client.CURRENT_AI_COMPETITION_ID, return_exceptions=True
            )
        )
        reports += asyncio.run(
            bot.forecast_on_tournament(
                client.CURRENT_MINIBENCH_ID, return_exceptions=True
            )
        )
    elif args.mode == "metaculus_cup":
        bot.skip_previously_forecasted_questions = False
        reports = asyncio.run(
            bot.forecast_on_tournament(
                client.CURRENT_METACULUS_CUP_ID, return_exceptions=True
            )
        )
    else:  # test_questions
        bot.skip_previously_forecasted_questions = False
        urls = [
            "https://www.metaculus.com/questions/578/human-extinction-by-2100/",
            "https://www.metaculus.com/questions/14333/age-of-oldest-human-as-of-2100/",
            "https://www.metaculus.com/questions/22427/number-of-new-leading-ai-labs/",
        ]
        questions = [client.get_question_by_url(u) for u in urls]
        reports = asyncio.run(bot.forecast_questions(questions, return_exceptions=True))

    bot.log_report_summary(reports)


if __name__ == "__main__":
    main()
