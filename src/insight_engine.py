import ollama


INSIGHT_PROMPT = """
You are a senior business analyst.

Your task is to generate a short business insight
based on a data analysis result.

Rules:
- Maximum 3 sentences.
- Be concise.
- Mention important trends or rankings.
- Do not invent numbers that are not provided.
- Use professional business language.
"""

def generate_ai_insight(query, result):
    try:

        prompt = f"""
User Question:
{query}

Analysis Result:
{result}

Generate a short business insight.
"""

        response = ollama.chat(
            model="llama3.2",
            messages=[
                {
                    "role": "system",
                    "content": INSIGHT_PROMPT
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            options={
                "temperature": 0.2
            }
        )

        return response["message"]["content"]

    except Exception:
        return (
            "AI insight is available in the local version using Ollama and llama3.2. "
            "This cloud demo uses the structured analysis engine for data results."
        )