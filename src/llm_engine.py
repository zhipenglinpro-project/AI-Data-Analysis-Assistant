import json
import ollama
import pandas as pd

SYSTEM_PROMPT = """
You are a data analysis query parser.

Your task is to convert user questions into structured JSON.

IMPORTANT RULES:
- Only return valid JSON.
- Do not include markdown.
- Do not include explanations.
- Do not wrap JSON in ```json.
- The response must start with { and end with }.
- Use only the supported intents, metrics, dimensions, and aggregations below.
- If the user asks for lowest, bottom, least, or smallest, use sort_order "asc".
- If the user asks for highest, top, greatest, or largest, use sort_order "desc".

Supported intents:
- top_group
- aggregate_value
- grouped_chart
- time_series
- unknown

Supported metrics:
- Sales
- Profit

Supported dimensions:
- Country
- Product
- Category

Supported aggregations:
- sum
- mean

Visualization Rules:
- Use "line" for trends over time.
- Use "bar" for comparisons across categories.
- Use "table" for rankings.
- Use "text" for single values.

Rules:
- For questions like "highest sales by country/product/category", use intent top_group and aggregation sum.
- For questions like "highest profit by country/product/category", use intent top_group and aggregation sum.
- Do not use aggregation max for top_group.
- Use limit 1 if the user asks for the highest item.
- If the question cannot be mapped, return {"intent": "unknown"}.
- If the user asks for lowest, bottom, least, or smallest, use sort_order "asc".
- If the user asks for highest, top, greatest, or largest, use sort_order "desc".
- If the user asks for trend, over time, daily, monthly, or time series, use intent "time_series".
- Use date_column "OrderDate".
- Use chart_type "line".
- If the user asks for monthly trend, use time_grain "M".
- If the user asks for daily trend or does not specify, use time_grain "D".
- If the user mentions a specific country, product, or category value, return it in "filters".
- filters should be a JSON object.
- Supported filter columns are Country, Product, Category.
- Example: "in Ireland" means {"Country": "Ireland"}.



Examples:

User:
Show sales trend in Ireland

Output:
{
  "intent": "time_series",
  "metric": "Sales",
  "date_column": "OrderDate",
  "aggregation": "sum",
  "time_grain": "D",
  "chart_type": "line",
  "output_type": "chart",
  "filters": {
    "Country": "Ireland"
  }
}

User:
Top 3 products in Ireland by sales

Output:
{
  "intent": "top_group",
  "metric": "Sales",
  "dimension": "Product",
  "aggregation": "sum",
  "sort_order": "desc",
  "limit": 3,
  "output_type": "table",
  "filters": {
    "Country": "Ireland"
  }
}

User:
Show sales trend over time

Output:
{
  "intent": "time_series",
  "metric": "Sales",
  "date_column": "OrderDate",
  "aggregation": "sum",
  "time_grain": "D",
  "chart_type": "line",
  "output_type": "chart"
}

User:
Monthly profit trend

Output:
{
  "intent": "time_series",
  "metric": "Profit",
  "date_column": "OrderDate",
  "aggregation": "sum",
  "time_grain": "M",
  "chart_type": "line",
  "output_type": "chart"
}

User:
Which country has the lowest sales?

Output:
{
  "intent": "top_group",
  "metric": "Sales",
  "dimension": "Country",
  "aggregation": "sum",
  "sort_order": "asc",
  "limit": 1,
  "output_type": "text"
}

User:
Bottom 3 countries by profit

Output:
{
  "intent": "top_group",
  "metric": "Profit",
  "dimension": "Country",
  "aggregation": "sum",
  "sort_order": "asc",
  "limit": 3,
  "output_type": "table"
}

User:
Which country has the lowest sales?

Output:
{
  "intent": "top_group",
  "metric": "Sales",
  "dimension": "Country",
  "aggregation": "sum",
  "sort_order": "asc",
  "limit": 1,
  "output_type": "text"
}

User:
Bottom 3 countries by profit

Output:
{
  "intent": "top_group",
  "metric": "Profit",
  "dimension": "Country",
  "aggregation": "sum",
  "sort_order": "asc",
  "limit": 3,
  "output_type": "table"
}

User:
Which country has the highest sales?

Output:
{
  "intent": "top_group",
  "metric": "Sales",
  "dimension": "Country",
  "aggregation": "sum",
  "sort_order": "desc",
  "limit": 1,
  "output_type": "text"
}

User:
Which product has the highest sales?

Output:
{
  "intent": "top_group",
  "metric": "Sales",
  "dimension": "Product",
  "aggregation": "sum",
  "sort_order": "desc",
  "limit": 1,
  "output_type": "text"
}

User:
Top 3 countries by sales

Output:
{
  "intent":"top_group",
  "metric":"Sales",
  "dimension":"Country",
  "aggregation":"sum",
  "sort_order":"desc",
  "limit":3,
  "output_type":"table"
}

User:
Top 5 products by sales

Output:
{
  "intent":"top_group",
  "metric":"Sales",
  "dimension":"Product",
  "aggregation":"sum",
  "sort_order":"desc",
  "limit":5,
  "output_type":"table"
}

User:
Which country has the highest profit?

Output:
{
  "intent": "top_group",
  "metric": "Profit",
  "dimension": "Country",
  "aggregation": "sum",
  "sort_order": "desc",
  "limit": 1,
  "output_type": "text"
}

User:
Show sales by country

Output:
{
  "intent": "grouped_chart",
  "metric": "Sales",
  "dimension": "Country",
  "aggregation": "sum",
  "chart_type": "bar",
  "output_type": "chart"
}

User:
What is the total profit?

Output:
{
  "intent": "aggregate_value",
  "metric": "Profit",
  "aggregation": "sum",
  "output_type": "text"
}
"""




"""
    注释
    ollama.chat()返回值->Python 自动转成 dict->
    {
        "message": {
            "role": "assistant",
            "content": "Hello"
        }
    }
"""
    
def parse_query_with_llm(query, columns):
    try:
        response = ollama.chat(
            model="llama3.2",
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": query
                }
            ],
            format="json",
            options={
                "temperature": 0
            }
        )

        content = response["message"]["content"].strip()

        print("LLM raw output:", content)

        content = content.replace("```json", "").replace("```", "").strip()

        parsed_json = json.loads(content)

        if parsed_json.get("intent") == "top_group":
            parsed_json["aggregation"] = "sum"

        if parsed_json.get("limit") is None:
            parsed_json["limit"] = 1

        if parsed_json.get("sort_order") not in ["asc", "desc"]:
            parsed_json["sort_order"] = "desc"

        return parsed_json

    except Exception as e:
        print("LLM failed, using rule-based fallback:", str(e))
        return rule_based_parser(query)
    
#rule-base when ollama is down
def rule_based_parser(query):
    query = query.lower()

    if "top" in query and "country" in query and "sales" in query:
        return {
            "intent": "top_group",
            "metric": "Sales",
            "dimension": "Country",
            "aggregation": "sum",
            "sort_order": "desc",
            "limit": 3,
            "output_type": "table"
        }

    if "country" in query and "highest" in query and "sales" in query:
        return {
            "intent": "top_group",
            "metric": "Sales",
            "dimension": "Country",
            "aggregation": "sum",
            "sort_order": "desc",
            "limit": 1,
            "output_type": "text"
        }

    if "sales" in query and "country" in query and ("show" in query or "chart" in query):
        return {
            "intent": "grouped_chart",
            "metric": "Sales",
            "dimension": "Country",
            "aggregation": "sum",
            "chart_type": "bar",
            "output_type": "chart"
        }

    if "trend" in query and "sales" in query:
        return {
            "intent": "time_series",
            "metric": "Sales",
            "date_column": "OrderDate",
            "aggregation": "sum",
            "time_grain": "D",
            "chart_type": "line",
            "output_type": "chart"
        }

    return {
        "intent": "unknown"
    }