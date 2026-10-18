
import os
import json

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

MODEL_NAME = "gemini-3.8-flash"

REQUIRED_KEYS = {
    "professional_summary",
    "skill_gap_report",
    "learning_roadmap",
    "interview_preparation",
}


def generate_career_package(skills, interests, education, target_role):
    """Generate a report using Gemini. Called only in Live AI mode."""

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is missing. Add it to your .env file "
            "to use Live AI mode. Demo Mode works without a key."
        )

    prompt = f"""
Create a concise, personalized career report.

Candidate:
- Skills: {skills}
- Interests: {interests}
- Education: {education}
- Target role: {target_role}

Return only valid JSON with exactly these four keys:

"professional_summary":
A personalized professional summary in 60-80 words.

"skill_gap_report":
Include 3 important skills to improve, why they matter,
and 2 practical project suggestions.

"learning_roadmap":
A 4-week plan. For each week, include one learning goal
and one hands-on task.

"interview_preparation":
Include 3 likely interview questions with short sample answers
and 2 preparation tips.

Use simple, specific, actionable language.
Do not invent qualifications or experience.
Return valid JSON only, without Markdown fences.
"""

    try:
        # Create the client only when Live AI mode is requested.
        client = genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(timeout=20000),
        )

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "max_output_tokens": 2500,
            },
        )

        if not response.text:
            raise RuntimeError("Gemini returned an empty response.")

        report = json.loads(response.text)

        if not isinstance(report, dict):
            raise RuntimeError("Gemini returned an invalid report format.")

        missing = REQUIRED_KEYS - report.keys()
        if missing:
            raise RuntimeError(
                "Gemini's response is missing sections: "
                + ", ".join(sorted(missing))
            )

        return report

    except json.JSONDecodeError as error:
        raise RuntimeError(
            "Gemini returned incomplete or invalid JSON. Please try again."
        ) from error

    except Exception as error:
        message = str(error).upper()

        if "429" in message or "RESOURCE_EXHAUSTED" in message:
            raise RuntimeError(
                "Gemini API quota is exhausted. Switch to Demo Mode to "
                "test the app without API calls, or wait for your quota reset."
            ) from error

        if any(code in message for code in (
            "503", "UNAVAILABLE", "TIMEOUT",
            "DEADLINE_EXCEEDED", "502", "504",
        )):
            raise RuntimeError(
                "Gemini is unavailable or the request timed out. "
                "Try again later, or use Demo Mode."
            ) from error

        if isinstance(error, RuntimeError):
            raise

        raise RuntimeError(
            f"Live AI generation failed ({type(error).__name__}): {error}"
        ) from error
