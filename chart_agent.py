import asyncio
from agents import Agent, AgentOutputSchemaBase, OpenAIChatCompletionsModel, RunResult, Runner, function_tool
from typing import Any, Dict, TypedDict, cast
import json
import re
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import io
import base64
from pydantic import BaseModel
from openai_client import client, AZURE_OPENAI_CHAT_DEPLOYMENT_MODEL


# Load instructions for the chart agent from the provided file. If the file
# is missing or unreadable, fall back to a concise default instruction set.
try:
    with open("chart_agent_instructions.txt", "r", encoding="utf-8") as f:
        chart_instructions = f.read().strip()
except Exception:
    print("Warning: chart_agent_instructions.txt file not found or unreadable. Using default instructions.")
    chart_instructions = (
        "You are a data visualization agent. Use the data provided in the input to create an array of dictionaries of"
        "pyplot methods and arguments which will be used to generate a chart with matplotlib.pyplot by another code block. "
    )


class ChartProps(BaseModel):
    kind: str
    x: list[str]
    y: list[float]
    xlabel: str
    ylabel: str


def create_plot(data: ChartProps) -> Figure:
    """Create a plot using matplotlib and return the figure."""
    print(
        f"Plotting {data.kind} chart with x: {data.x} and y: {data.y}")

    fig, ax = plt.subplots()
    if data.kind == 'bar':
        ax.bar(data.x, data.y, width=2)
    elif data.kind == 'scatter':
        ax.scatter(data.x, data.y)
    elif data.kind == 'hist':
        # Histogram typically uses only y values
        ax.hist(data.y, bins=10)
    elif data.kind == 'pie':
        ax.pie(data.y, labels=data.x, autopct='%1.1f%%')  # Pie chart
    else:  # Default to line plot
        ax.plot(data.x, data.y)
    ax.set_xlabel(data.xlabel)
    ax.set_ylabel(data.ylabel)

    return fig


chart_maker_agent = Agent(
    name="chart-agent",
    instructions=chart_instructions,
    model=OpenAIChatCompletionsModel(
        model=cast(str, AZURE_OPENAI_CHAT_DEPLOYMENT_MODEL),
        openai_client=client,
    ),
    output_type=ChartProps,
)


async def main(user_input: Dict[str, Any] | None = None, prompt: str | None = None) -> Figure | None:
    """Run the chart agent with user input (expects a dict).

    The runner expects a string input, so serialize the dict to JSON.
    """
    if user_input is None:
        print("Please provide user input (a dict with data and chart instructions).")
        return

    result = await Runner.run(
        chart_maker_agent,
        input=json.dumps({"data": user_input, "prompt": prompt}),
        max_turns=20,
    )
    print(
        f"Chart Agent execution completed with result: {result.final_output}")

    chart = create_plot(result.final_output)

    return chart


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Error running chart agent: {e}")
