import json
import chainlit as cl
from program import main as digest_nlp
from chart_agent import main as make_chart
import matplotlib.pyplot as plt


@cl.step(type="tool")
async def tool(user_input: str):
    result = await digest_nlp(user_input)
    return result


@cl.action_callback("show_raw_output")
async def show_raw_output(action: cl.Action):
    await cl.Message(content=f"{action.payload['data']}").send()


async def prompt_action(rawResult: str):
    # Sending an action button within a chatbot message
    actions = [
        cl.Action(
            name="show_raw_output",
            icon="mouse-pointer-click",
            payload={"data": rawResult},
            label="Show Raw Results"
        )
    ]

    await cl.Message(content="Outputs are in `JSON` format by default. Click the button below to see the raw output.", actions=actions).send()


def render_chart(coords: list):
    print(coords)
    fig, ax = plt.subplots()
    ax.plot(coords[0], coords[1])
    return fig


@cl.on_message
async def main(message: cl.Message):
    result = await tool(message.content)
    if result is not None:
        await cl.Message(content=result.final_output).send()
        fig = await make_chart(result.final_output, message.content)
        elements = [cl.Pyplot(name="Generated Chart",
                              figure=fig, size="large", display="inline")]
        await cl.Message(content=f"Chart generation result: {fig}", elements=elements).send()
    else:
        await cl.Message(content="I could not generate the chart.").send()
