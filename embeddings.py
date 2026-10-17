from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()


def embed(text):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text,
    )
    return response.data[0].embedding


def similarity(a, b):
    total = 0
    for x, y in zip(a, b):
        total += x * y
    return total