from src.llm_engine import parse_query_with_llm
import pandas as pd
from src.context_engine import enrich_query_with_context

TEXT_QUESTIONS = [
    "Which country has the highest sales?",
    "Which product has the highest sales?",
    "Which country has the highest profit?",
    "Which category has the highest sales?",
    "What is the average sales?",
    "What is the total profit?"
]

CHART_QUESTIONS = [
    "Show sales by country",
    "Show sales by category",
    "Show profit by country"
]

#回答问题
def get_top_group(df, group_column, metric_column):
    grouped_data = df.groupby(group_column)[metric_column].sum()

    top_name = grouped_data.idxmax()
    top_value = grouped_data.max()

    return top_name, top_value

def answer_question(df, query):
    query = query.lower()

    if "country" in query and "highest" in query and "sales" in query:
        top_country, top_sales = get_top_group(df, "Country", "Sales")

        return {
            "status": "success",
            "type": "text",
            "message": f"{top_country} has the highest sales: {top_sales:.2f}",
            "metric": "Sales",
            "dimension": "Country",
            "label": top_country,
            "value": top_sales
        }

    elif "product" in query and "highest" in query and "sales" in query:
        top_product, top_sales = get_top_group(df, "Product", "Sales")

        return {
            "status": "success",
            "type": "text",
            "message": f"{top_product} has the highest sales: {top_sales:.2f}",
            "metric": "Sales",
            "dimension": "Product",
            "label": top_product,
            "value": top_sales
        }

    elif "country" in query and "highest" in query and "profit" in query:
        top_country, top_profit = get_top_group(df, "Country", "Profit")

        return {
            "status": "success",
            "type": "text",
            "message": f"{top_country} has the highest profit: {top_profit:.2f}",
            "metric": "Profit",
            "dimension": "Country",
            "label": top_country,
            "value": top_profit
        }

    elif "category" in query and "highest" in query and "sales" in query:
        top_category, top_sales = get_top_group(df, "Category", "Sales")

        return {
            "status": "success",
            "type": "text",
            "message": f"{top_category} has the highest sales: {top_sales:.2f}",
            "metric": "Sales",
            "dimension": "Category",
            "label": top_category,
            "value": top_sales
        }

    elif "average" in query and "sales" in query:
        avg_sales = df["Sales"].mean()

        return {
            "status": "success",
            "type": "text",
            "message": f"The average sales is: {avg_sales:.2f}",
            "metric": "Sales",
            "dimension": None,
            "label": "Average Sales",
            "value": avg_sales

        }

    elif "total" in query and "profit" in query:
        total_profit = df["Profit"].sum()

        return {
            "status": "success",
            "type": "text",
            "message": f"The total profit is: {total_profit:.2f}",
            "metric": "Profit",
            "dimension": None,
            "label": "Total Profit",
            "value": total_profit
        }

    else:
        return {
            "status": "error",
            "type": "text",
            "message": "Sorry, I cannot understand this question yet.",
            "metric": None,
            "dimension": None,
            "label": None,
            "value": None
        }



#画图
def get_grouped_data(df, group_column, metric_column):
    return df.groupby(group_column)[metric_column].sum()


def generate_chart_data(df, query):
    query = query.lower()

    if ("show" in query or "chart" in query) and "sales" in query and "country" in query:
        data = get_grouped_data(df, "Country", "Sales")
        top_country, top_sales = get_top_group(df, "Country", "Sales")

        return {
            "status": "success",
            "type": "chart",
            "chart_type": "bar",
            "data": data,
            "title": "Sales by Country",
            "xlabel": "Country",
            "ylabel": "Total Sales",
            "explanation": f"{top_country} has the highest total sales: {top_sales:.2f}"
        }

    elif ("show" in query or "chart" in query) and "sales" in query and "category" in query:
        data = get_grouped_data(df, "Category", "Sales")
        top_category, top_sales = get_top_group(df, "Category", "Sales")

        return {
            "status": "success",
            "type": "chart",
            "chart_type": "bar",
            "data": data,
            "title": "Sales by Category",
            "xlabel": "Category",
            "ylabel": "Total Sales",
            "explanation": f"{top_category} has the highest total sales: {top_sales:.2f}"
        }

    elif ("show" in query or "chart" in query) and "profit" in query and "country" in query:
        data = get_grouped_data(df, "Country", "Profit")
        top_country, top_profit = get_top_group(df, "Country", "Profit")

        return {
            "status": "success",
            "type": "chart",
            "chart_type": "bar",
            "data": data,
            "title": "Profit by Country",
            "xlabel": "Country",
            "ylabel": "Total Profit",
            "explanation": f"{top_country} has the highest total profit: {top_profit:.2f}"
        }

    else:
        return None
    



def generate_business_insights(df):
    insights = {}

    total_sales = df["Sales"].sum()
    total_profit = df["Profit"].sum()
    profit_margin = total_profit / total_sales * 100

    country_sales = df.groupby("Country")["Sales"].sum()
    product_sales = df.groupby("Product")["Sales"].sum()
    category_profit = df.groupby("Category")["Profit"].sum()

    insights["total_sales"] = total_sales
    insights["total_profit"] = total_profit
    insights["profit_margin"] = profit_margin

    insights["top_country"] = country_sales.idxmax()
    insights["top_country_sales"] = country_sales.max()

    insights["top_product"] = product_sales.idxmax()
    insights["top_product_sales"] = product_sales.max()

    insights["top_category_profit"] = category_profit.idxmax()
    insights["top_category_profit_value"] = category_profit.max()

    return insights

def get_supported_questions():
    return {
        "text": TEXT_QUESTIONS,
        "chart": CHART_QUESTIONS
    }


##deal with query
def handle_query(df, query,last_parsed_query=None):
    
    parsed_query = parse_query_with_llm(
        query,
        df.columns
    )


    parsed_query = enrich_query_with_context(
        parsed_query,
        last_parsed_query
    )

    #llm判断意图成功，执行结构化query
    if parsed_query.get("intent") != "unknown":
        result = execute_structured_query(df, parsed_query)
        result["parsed_query"] = parsed_query
        return result

    #llm判断失败，直接尝试画图或者回答
    #画图
    chart_result = generate_chart_data(df, query)

    if chart_result is not None:
        chart_result["parsed_query"] = parsed_query
        return chart_result

    #回答
    answer_result = answer_question(df, query)
    answer_result["parsed_query"] = parsed_query

    return answer_result


# 过滤功能
def apply_filters(df, filters):
    if not filters:
        return df

    filtered_df = df.copy()

    for column, value in filters.items():
        if column in filtered_df.columns:
            filtered_df = filtered_df[
                filtered_df[column].astype(str).str.lower() == str(value).lower()
            ]

    return filtered_df

#编辑返回的filter message
def format_filter_text(filters):
    if not filters:
        return ""

    filter_parts = []

    for column, value in filters.items():
        filter_parts.append(f"{column} = {value}")

    return " with filter: " + ", ".join(filter_parts)


#执行结构query的要求
def execute_structured_query(df, parsed_query):

    intent = parsed_query.get("intent")

    # Apply filters
    filters = parsed_query.get("filters", {})
    df = apply_filters(df, filters)
    filter_text = format_filter_text(filters)

    if df.empty:
        return {
            "status": "error",
            "type": "text",
            "message": "No data found for the selected filter."
        }

    # ==========================
    # TOP GROUP
    # ==========================

    if intent == "top_group":

        metric = parsed_query.get("metric")
        dimension = parsed_query.get("dimension")
        aggregation = parsed_query.get("aggregation", "sum")
        limit = parsed_query.get("limit", 1)
        sort_order = parsed_query.get("sort_order", "desc")

        ascending = True if sort_order == "asc" else False

        if aggregation == "sum":
            grouped_data = df.groupby(dimension)[metric].sum()

        elif aggregation == "mean":
            grouped_data = df.groupby(dimension)[metric].mean()

        else:
            return {
                "status": "error",
                "type": "text",
                "message": f"Unsupported aggregation: {aggregation}"
            }

        result_data = grouped_data.sort_values(
            ascending=ascending
        ).head(limit)

        # Top N / Bottom N Table
        if limit > 1:

            result_table = result_data.reset_index()
            result_table.columns = [dimension, metric]

            result_table.insert(
                0,
                "Rank",
                range(1, len(result_table) + 1)
            )

            table_label = (
                "Bottom"
                if sort_order == "asc"
                else "Top"
            )

            return {
                "status": "success",
                "type": "table",
                "visualization": "table",
                "metric": metric,
                "dimension": dimension,
                "data": result_table,
                "message": (
                    f"{table_label} {limit} "
                    f"{dimension} by {metric}"
                    f"{filter_text}"
                )
            }

        # Single Result

        top_label = result_data.index[0]
        top_value = result_data.iloc[0]

        rank_word = (
            "lowest"
            if sort_order == "asc"
            else "highest"
        )

        return {
            "status": "success",
            "type": "text",
            "visualization": "text",
            "message": (
                f"{top_label} has the "
                f"{rank_word} {metric}: "
                f"{top_value:.2f}"
                f"{filter_text}"
            ),
            "metric": metric,
            "dimension": dimension,
            "label": top_label,
            "value": top_value
        }

    # ==========================
    # AGGREGATE VALUE
    # ==========================

    elif intent == "aggregate_value":

        metric = parsed_query.get("metric")
        aggregation = parsed_query.get("aggregation")

        if aggregation == "sum":
            value = df[metric].sum()
            label = f"Total {metric}"

        elif aggregation == "mean":
            value = df[metric].mean()
            label = f"Average {metric}"

        else:
            return {
                "status": "error",
                "type": "text",
                "message": f"Unsupported aggregation: {aggregation}"
            }

        return {
            "status": "success",
            "type": "text",
            "visualization": "text",
            "message": (
                f"{label}: "
                f"{value:.2f}"
                f"{filter_text}"
            ),
            "metric": metric,
            "dimension": None,
            "label": label,
            "value": value
        }

    # ==========================
    # GROUPED CHART
    # ==========================

    elif intent == "grouped_chart":

        metric = parsed_query.get("metric")
        dimension = parsed_query.get("dimension")
        aggregation = parsed_query.get("aggregation", "sum")
        chart_type = parsed_query.get("chart_type", "bar")

        if aggregation == "sum":
            grouped_data = df.groupby(dimension)[metric].sum()

        elif aggregation == "mean":
            grouped_data = df.groupby(dimension)[metric].mean()

        else:
            return {
                "status": "error",
                "type": "text",
                "message": f"Unsupported aggregation: {aggregation}"
            }

        top_label = grouped_data.idxmax()
        top_value = grouped_data.max()

        return {
            "status": "success",
            "type": "chart",
            "chart_type": chart_type,
            "visualization": "bar",
            "data": grouped_data,
            "title": f"{metric} by {dimension}",
            "xlabel": dimension,
            "ylabel": metric,
            "explanation": (
                f"{top_label} has the highest "
                f"total {metric}: "
                f"{top_value:.2f}"
                f"{filter_text}"
            )
        }

    # ==========================
    # TIME SERIES
    # ==========================

    elif intent == "time_series":

        metric = parsed_query.get("metric")
        date_column = parsed_query.get(
            "date_column",
            "OrderDate"
        )

        aggregation = parsed_query.get(
            "aggregation",
            "sum"
        )

        time_grain = parsed_query.get(
            "time_grain",
            "D"
        )

        chart_type = parsed_query.get(
            "chart_type",
            "line"
        )

        df_time = df.copy()

        df_time[date_column] = pd.to_datetime(
            df_time[date_column]
        )

        if aggregation == "sum":

            if time_grain == "M":
                grouped_data = (
                    df_time
                    .set_index(date_column)
                    .resample("ME")[metric]
                    .sum()
                )

                title_grain = "Monthly"

            else:
                grouped_data = (
                    df_time
                    .groupby(date_column)[metric]
                    .sum()
                )

                title_grain = "Daily"

        elif aggregation == "mean":

            if time_grain == "M":
                grouped_data = (
                    df_time
                    .set_index(date_column)
                    .resample("ME")[metric]
                    .mean()
                )

                title_grain = "Monthly"

            else:
                grouped_data = (
                    df_time
                    .groupby(date_column)[metric]
                    .mean()
                )

                title_grain = "Daily"

        else:
            return {
                "status": "error",
                "type": "text",
                "message": f"Unsupported aggregation: {aggregation}"
            }

        return {
            "status": "success",
            "type": "chart",
            "chart_type": chart_type,
            "visualization": "line",
            "data": grouped_data,
            "title": f"{title_grain} {metric} Trend",
            "xlabel": date_column,
            "ylabel": metric,
            "explanation": (
                f"This chart shows the "
                f"{title_grain.lower()} "
                f"{metric.lower()} trend "
                f"over time"
                f"{filter_text}."
            )
        }

    # ==========================
    # UNKNOWN
    # ==========================

    return {
        "status": "error",
        "type": "text",
        "message": "Sorry, I could not understand this question."
    }