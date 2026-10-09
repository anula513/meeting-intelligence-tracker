from parser import parse_transcript
from prompts import EXTRACTION_PROMPT
from schemas import Decision, ActionItem
from pydantic import BaseModel
from dotenv import load_dotenv
import os
from openai import OpenAI


load_dotenv()

# Create the client
client = OpenAI()

# Read the model name from .env
MODEL = os.getenv("OPENAI_MODEL")


class Extraction(BaseModel):
    decisions: list[Decision]
    action_items: list[ActionItem]


def extract(transcript_text):
    turns = parse_transcript(transcript_text)

    lines = []
    for number, turn in enumerate(turns, start=1):
        speaker = turn["speaker"] or "Unknown"
        line = f"[{number}] {speaker}: {turn['text']}"
        lines.append(line)

    numbered_text = "\n".join(lines)

    response = client.responses.parse(
        model=MODEL,
        input=[
            {"role": "system", "content": EXTRACTION_PROMPT},
            {"role": "user", "content": numbered_text},
        ],
        text_format=Extraction,
    )

    result = response.output_parsed
    if result is None:
        raise ValueError("The model did not return a valid extraction.")
    return result

    