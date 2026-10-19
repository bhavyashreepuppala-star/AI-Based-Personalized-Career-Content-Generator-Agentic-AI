
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
    """Generate a career report using Gemini in Live AI mode."""

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is missing. Check your local .env file."
        )

    prompt = f"""
Create a concise, personalized career report.

Candidate:
- Skills: {skills}
- Interests: {interests}
- Education: {education}
- Target role: {target_role}

Return valid JSON with exactly these four keys:
1. professional_summary: A personalized summary in 60-80 words.
2. skill_gap_report: Three skills to improve, why they matter,
   and two practical project suggestions.
3. learning_roadmap: A four-week plan with one learning goal
   and one hands-on task per week.
4. interview_preparation: Three likely interview questions
   with short sample answers and two preparation tips.

Use simple, specific, actionable language.
Do not invent qualifications or experience.
Return JSON only, without Markdown fences.
"""

    try:
        client = genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(timeout=60000),
        )

        interaction = client.interactions.create(
            model=MODEL_NAME,
            input=prompt,
            response_format={
                "type": "text",
                "mime_type": "application/json",
                "schema": {
                    "type": "object",
                    "properties": {
                        "professional_summary": {"type": "string"},
                        "skill_gap_report": {"type": "string"},
                        "learning_roadmap": {"type": "string"},
                        "interview_preparation": {"type": "string"},
                    },
                    "required": sorted(REQUIRED_KEYS),
                },
            },
        )

        if not interaction.output_text:
            raise RuntimeError("Gemini returned an empty response.")

        report = json.loads(interaction.output_text)

        if not isinstance(report, dict):
            raise RuntimeError("Gemini returned an invalid report format.")

        missing = REQUIRED_KEYS - report.keys()
        if missing:
            raise RuntimeError(
                "Gemini response is missing sections: "
                + ", ".join(sorted(missing))
            )

        return report

    except json.JSONDecodeError as error:
        raise RuntimeError(
            "Gemini returned invalid JSON. Please try again."
        ) from error

    except Exception as error:
        # Preserve the original API error for diagnosis.
        message = str(error)
        upper_message = message.upper()

        if "429" in upper_message or "RESOURCE_EXHAUSTED" in upper_message:
            reason = "Gemini reported a quota or rate-limit error."
        elif "404" in upper_message or "NOT_FOUND" in upper_message:
            reason = "Gemini reported that a model or API resource was not found."
        elif "503" in upper_message or "UNAVAILABLE" in upper_message:
            reason = "Gemini is temporarily unavailable."
        elif any(code in upper_message for code in ("504", "DEADLINE_EXCEEDED", "TIMEOUT")):
            reason = "The Gemini request timed out."
        elif "401" in upper_message or "403" in upper_message or "API_KEY" in upper_message:
            reason = "Check the API key and its permissions."
        else:
            reason = "Gemini request failed."

        # The original exception is included for local troubleshooting.
        raise RuntimeError(
            f"{reason} Original error: {type(error).__name__}: {message}"
        ) from error
