import streamlit as st
import pandas as pd
#import matplotlib.pyplot as plt
from src.chart_generator import create_interactive_bar_chart,create_interactive_line_chart
from src.analysis_engine import handle_query, generate_business_insights, get_supported_questions
from src.data_loader import load_data
from src.data_profiler import get_data_overview, validate_required_columns, validate_data_types, clean_data
from src.insight_engine import generate_ai_insight
from src.report_engine import generate_executive_report
from src.context_engine import enrich_query_with_context

#创建session_state存query_history / executive report 列表
if "query_history" not in st.session_state:
    st.session_state.query_history = []


if "last_query" not in st.session_state:
    st.session_state.last_query = None

#report
if "executive_report" not in st.session_state:
    st.session_state.executive_report = None

#for multi-turn context
if "last_parsed_query" not in st.session_state:
    st.session_state.last_parsed_query = None

#A 基本网页结构，上传入口
st.set_page_config(
    page_title="AI Data Analysis Assistant",
    page_icon="📊",
    layout="wide"
)

st.title("📊 AI Data Analysis Assistant")
st.markdown(
    """
    This AI Data Analysis Assistant helps users upload sales datasets, 
    explore business performance, ask natural language questions, 
    generate charts, and create AI-powered business insights.
    """
)

st.write("Upload your dataset and ask questions about your data.")

# File uploader
uploaded_file = st.file_uploader(
    "Upload a CSV or Excel file",
    type=["csv", "xlsx"]
)

# If user uploads a file
if uploaded_file is not None:

    df, error = load_data(uploaded_file)

    #检查文件类型
    if error:
        st.error(f"Failed to load file: {error}")
        st.stop()

    st.success("File uploaded successfully!")

    #检查有没有缺少必要的列
    required_columns = [
        "OrderDate",
        "Country",
        "Category",
        "Product",
        "Sales",
        "Profit"
    ]

    missing_columns = validate_required_columns(df, required_columns)

    if missing_columns:
        st.error(
            f"The uploaded file is missing required columns: {', '.join(missing_columns)}"
        )
        st.stop()

    type_errors = validate_data_types(df)

    if type_errors:
        for error in type_errors:
            st.error(error)

        st.stop()

    df = clean_data(df)

    # deal with filter data
    filtered_df = df.copy()

    #sidebar-explanation
    st.sidebar.title("AI Data Analysis Assistant")

    st.sidebar.markdown(
        """
        **Features**
        - Upload CSV / Excel data
        - Explore data overview
        - Generate business insights
        - Ask natural language questions
        - Create AI-powered reports
        """
    )


    #sidebar - data filter
    st.sidebar.header("Dashboard Filters")

    country_options = sorted(df["Country"].unique())
    selected_countries = st.sidebar.multiselect(
        "Select Country",
        country_options,
        default=country_options
    )

    category_options = sorted(df["Category"].unique())
    selected_categories = st.sidebar.multiselect(
        "Select Category",
        category_options,
        default=category_options
    )

    date_min = df["OrderDate"].min()
    date_max = df["OrderDate"].max()

    selected_date_range = st.sidebar.date_input(
        "Select Date Range",
        value=(date_min, date_max)
    )

    #apply filter
    filtered_df = filtered_df[
        filtered_df["Country"].isin(selected_countries)
    ]

    filtered_df = filtered_df[
        filtered_df["Category"].isin(selected_categories)
    ]

    if len(selected_date_range) == 2:
        start_date, end_date = selected_date_range

        filtered_df = filtered_df[
            (filtered_df["OrderDate"].dt.date >= start_date)
            & (filtered_df["OrderDate"].dt.date <= end_date)
        ]

    if filtered_df.empty:
        st.warning("No data available for the selected filters.")
        st.stop()

    st.sidebar.markdown("---")
    st.sidebar.subheader("Current Selection")

    st.sidebar.write(f"Countries: {len(selected_countries)} selected")
    st.sidebar.write(f"Categories: {len(selected_categories)} selected")
    st.sidebar.write(f"Rows after filtering: {filtered_df.shape[0]}")

    
    #dash bar starts here
    st.subheader("Dashboard Summary")

    summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)

    with summary_col1:
        st.metric("Rows", filtered_df.shape[0])

    with summary_col2:
        st.metric("Total Sales", f"{filtered_df['Sales'].sum():.2f}")

    with summary_col3:
        st.metric("Total Profit", f"{filtered_df['Profit'].sum():.2f}")

    with summary_col4:
        profit_margin = filtered_df["Profit"].sum() / filtered_df["Sales"].sum() * 100
        st.metric("Profit Margin", f"{profit_margin:.2f}%")
    
    #tab
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Preview",
        "Overview",
        "Insights",
        "Charts",
        "Ask Questions"
    ])
    with tab1:
        st.subheader("Dataset Preview")
        st.dataframe(filtered_df.head())

    with tab2:
        overview = get_data_overview(filtered_df)

        st.subheader("Data Overview")

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Rows", overview["rows"])

        with col2:
            st.metric("Columns", overview["columns"])

        st.subheader("Column Information")
        st.write(overview["column_info"])

        st.subheader("Missing Values")
        st.write(overview["missing_values"])

        st.subheader("Statistical Summary")
        st.dataframe(overview["statistics"])

    with tab3:
        st.subheader("Business Insights")

        insights = generate_business_insights(filtered_df)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total Sales", f"{insights['total_sales']:.2f}")

        with col2:
            st.metric("Total Profit", f"{insights['total_profit']:.2f}")

        with col3:
            st.metric("Profit Margin", f"{insights['profit_margin']:.2f}%")

        st.write(
            f"Top country by sales is **{insights['top_country']}**, "
            f"with total sales of **{insights['top_country_sales']:.2f}**."
        )

        st.write(
            f"Top product by sales is **{insights['top_product']}**, "
            f"with total sales of **{insights['top_product_sales']:.2f}**."
        )

        st.write(
            f"Most profitable category is **{insights['top_category_profit']}**, "
            f"with total profit of **{insights['top_category_profit_value']:.2f}**."
        )

        # AI Executive Report
        st.subheader("AI Executive Report")

        if st.button("Generate Executive Report"):
            with st.spinner("Generating executive report..."):
                st.session_state.executive_report = generate_executive_report(insights)

        if st.session_state.executive_report:

            st.markdown(
                st.session_state.executive_report
            )

            #download report
            report_text = st.session_state.executive_report

            st.download_button(
                label="Download Report (.md)",
                data=report_text,
                file_name="executive_report.md",
                mime="text/markdown"
            )

            st.download_button(
                label="Download Report (.txt)",
                data=report_text,
                file_name="executive_report.txt",
                mime="text/plain"
            )

            if st.button("Clear Executive Report"):
                st.session_state.executive_report = None
                st.rerun()

    with tab4:
        st.subheader("Sales by Category")

        category_sales = filtered_df.groupby("Category")["Sales"].sum()

        fig = create_interactive_bar_chart(
            category_sales,
            "Total Sales by Category",
            "Category",
            "Total Sales"
        )

        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Sales by Country")

        country_sales = filtered_df.groupby("Country")["Sales"].sum()

        fig = create_interactive_bar_chart(
            country_sales,
            "Total Sales by Country",
            "Country",
            "Total Sales"
        )

        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Sales Trend Over Time")

        daily_sales = filtered_df.groupby("OrderDate")["Sales"].sum()

        fig = create_interactive_line_chart(
            daily_sales,
            "Daily Sales Trend",
            "Order Date",
            "Total Sales"
        )

        st.plotly_chart(fig, use_container_width=True)

    with tab5:
        st.subheader("Ask Questions About Your Data")

        st.caption(
            "Ask questions such as ranking, comparison, trend, or filtered analysis. "
            "Examples: Top 3 countries by sales, Show sales trend in Ireland, "
            "Bottom 5 products by profit."
        )

        st.write("Click an example question or enter your own question:")

        supported_questions = get_supported_questions()

        selected_question = None

        st.markdown("### Text Questions")

        for question in supported_questions["text"]:
            if st.button(question):
                selected_question = question

        st.markdown("### Chart Questions")

        for question in supported_questions["chart"]:
            if st.button(question):
                selected_question = question

        custom_query = st.text_input(
            "Enter your question",
            placeholder="e.g. Which country has the highest sales?"
        )

        query = selected_question if selected_question else custom_query

        if query:
            result = handle_query(
                filtered_df,
                query,
                st.session_state.last_parsed_query
            )

            #store last query for multi-turn context
            if "parsed_query" in result:
                st.session_state.last_parsed_query = result["parsed_query"]
            
            #将与前一次问答不同的问答（即去重）存入query_history
            if query != st.session_state.last_query:

                st.session_state.query_history.append(
                    {
                        "query": query,
                        "result": result
                    }
                )

                st.session_state.last_query = query

                # 显示当前问题
                st.markdown(f"**Q:** {query}")

                # 显示回答
                if result["status"] == "error":
                    st.warning(result["message"])

                elif result["type"] == "text":
                    st.success(result["message"])

                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.metric("Metric", result.get("metric", "N/A"))

                    with col2:
                        st.metric("Dimension", result.get("dimension", "N/A"))

                    with col3:
                        st.metric("Value", f"{result.get('value', 0):.2f}")


                elif result["type"] == "table":
                    st.success(result.get("message", "Table result generated."))
                    st.dataframe(result["data"], use_container_width=True)


                elif result["type"] == "chart":
                    if result["chart_type"] == "bar":
                        fig = create_interactive_bar_chart(
                            result["data"],
                            result["title"],
                            result["xlabel"],
                            result["ylabel"]
                        )

                        st.plotly_chart(fig, use_container_width=True)
                        st.info(result["explanation"])

                    elif result["chart_type"] == "line":
                        fig = create_interactive_line_chart(
                            result["data"],
                            result["title"],
                            result["xlabel"],
                            result["ylabel"]
                        )

                        st.plotly_chart(fig, use_container_width=True)
                        st.info(result["explanation"])

            #show ai insight
            if result["status"] == "success":

                with st.spinner("Generating AI insight..."):
                    insight = generate_ai_insight(
                        query,
                        result
                    )

                st.subheader("AI Insight")

                st.info(insight)

            #show json & Visualization type
            
            st.caption(
                "The parsed query below shows how the LLM converts your natural language question into a structured analysis task."
            )
            
            with st.expander("Debug: Parsed Query"):
                st.json(result.get("parsed_query", {}))
            st.caption(
                f"Visualization: {result.get('visualization', 'N/A')}"
            )

        #显示query_history
        st.subheader("Query History")

        if st.button("Clear History"):
            st.session_state.query_history = []
            st.rerun()

        if len(st.session_state.query_history) > 1:
            for item in reversed(st.session_state.query_history[:-1]):
                st.markdown(f"**Q:** {item['query']}")

                result = item["result"]

                if result["status"] == "success":
                    if result["type"] == "text":
                        st.markdown(f"**A:** {result['message']}")
                    elif result["type"] == "chart":
                        st.markdown(f"**A:** Generated chart - {result['title']}")
                else:
                    st.markdown(f"**A:** {result['message']}")
                with st.expander("Parsed Query"):
                    st.json(result.get("parsed_query", {}))

                st.divider()
        else:
            st.caption("No questions asked yet.")

        
        #导出query history
        if st.session_state.query_history:
            export_rows = []

            for item in st.session_state.query_history:
                result = item["result"]

                export_rows.append(
                    {
                        "Question": item["query"],
                        "Status": result.get("status"),
                        "Type": result.get("type"),
                        "Answer": result.get("message", result.get("title", "")),
                        "Metric": result.get("metric", ""),
                        "Dimension": result.get("dimension", ""),
                        "Value": result.get("value", ""),
                        "parsed_query": result.get("parsed_query", {})
                    }
                )

            history_df = pd.DataFrame(export_rows)

            csv = history_df.to_csv(index=False).encode("utf-8")

            st.download_button(
                label="Download Query History as CSV",
                data=csv,
                file_name="query_history.csv",
                mime="text/csv"
            )


