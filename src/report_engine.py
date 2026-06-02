import ollama


REPORT_PROMPT = """
You are a senior business analyst.

Your task is to generate a concise executive report based on dataset insights.

Rules:
- Use professional business language.
- Do not invent numbers.
- Only use the information provided.
- Keep the report concise.
- Structure the report with:
  1. Executive Summary
  2. Key Findings
  3. Recommendations
"""


def generate_executive_report(insights):
    try:
        prompt = f"""
Dataset Business Insights:
{insights}

Generate an executive report based on the insights above.
"""

        response = ollama.chat(
            model="llama3.2",
            messages=[
                {
                    "role": "system",
                    "content": REPORT_PROMPT
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

    except Exception as e:
        return f"Report generation failed: {str(e)}"
    