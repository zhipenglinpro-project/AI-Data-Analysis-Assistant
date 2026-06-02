import matplotlib.pyplot as plt
import plotly.express as px


def create_interactive_bar_chart(data, title, xlabel, ylabel):
    chart_df = data.reset_index()
    chart_df.columns = [xlabel, ylabel]

    fig = px.bar(
        chart_df,
        x=xlabel,
        y=ylabel,
        title=title
    )

    fig.update_layout(
        xaxis_title=xlabel,
        yaxis_title=ylabel
    )

    return fig


def create_interactive_line_chart(data, title, xlabel, ylabel):
    chart_df = data.reset_index()
    chart_df.columns = [xlabel, ylabel]

    fig = px.line(
        chart_df,
        x=xlabel,
        y=ylabel,
        title=title,
        markers=True
    )

    fig.update_layout(
        xaxis_title=xlabel,
        yaxis_title=ylabel
    )

    return fig

def create_bar_chart(data, title, xlabel, ylabel):
    fig, ax = plt.subplots(figsize=(6, 4))

    ax.bar(data.index, data.values)

    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

    ax.tick_params(axis="x", rotation=45)
    ax.grid(True)

    plt.tight_layout()

    return fig


def create_line_chart(data, title, xlabel, ylabel):
    fig, ax = plt.subplots(figsize=(8, 4))

    ax.plot(data.index, data.values, marker="o")

    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

    ax.tick_params(axis="x", rotation=45)
    ax.grid(True)

    plt.tight_layout()

    return fig