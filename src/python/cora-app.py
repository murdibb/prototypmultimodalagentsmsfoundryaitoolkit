"""Connect model with mcp tools in Python
# Run this python script
> pip install openai-agents==0.*
> python <this-script-path>.py
"""
import asyncio
import base64
import json
import logging
import os
import sys
from typing import Any

from agents import Agent, AgentOutputSchemaBase, ModelSettings, OpenAIChatCompletionsModel, Runner, set_tracing_disabled
from agents.mcp import MCPServerSse, MCPServerStdio

from openai import AsyncAzureOpenAI

def encodeImage(path, mime_type):
    with open(path, "rb") as image:
        encoded = base64.b64encode(image.read())
    return f"data:{mime_type};base64,{encoded.decode()}"

async def main():
    openaiClient = AsyncAzureOpenAI(
        azure_endpoint = "https://aifoundry-61808571.openai.azure.com",
        api_key = os.environ["CUSTOM_OPENAI_API_KEY"],
        api_version = "2024-12-01-preview",
    )

    # init MCP servers
    servers = [
        MCPServerStdio(
            params = {
                "command": "INSERT_COMMAND_HERE",
                "args": [
                    "INSERT_ARGUMENTS_HERE",
                ],
                "env": {
                }
            },
            name = "VSCode Tools",
            client_session_timeout_seconds = 30,
        ),
    ]

    # setup logger
    logger = logging.getLogger("openai.agents")
    logger.setLevel(logging.DEBUG)
    logHandler = logging.StreamHandler(sys.stdout)
    logHandler.setFormatter(logging.Formatter('[Agent Log]: %(message)s'))
    logger.addHandler(logHandler)
    set_tracing_disabled(True)

    agent = Agent(
        name = "agent",
        instructions = "You are Cora, an intelligent and friendly AI assistant for Zava, a home improvement brand. You help customers with their DIY projects by understanding their needs and recommending the most suitable products from Zava's catalog.\nYour role is to:\n- Engage with the customer in natural conversation to understand their DIY goals.\n- Ask thoughtful questions to gather relevant project details.\n- Be brief in your responses.\n- Provide the best solution for the customer's problem and only recommend a relevant product within Zava's product catalog.\n- Search Zava's product database to identify 1 product that best match the customer's needs.\n- Clearly explain what each recommended Zava product is, why it's a good fit, and how it helps with their project.\n\nYour personality is:\n- Warm and welcoming, like a helpful store associate\n- Professional and knowledgeable, like a seasoned DIY expert\n- Curious and conversational-never assume, always clarify\n- Transparent and honest-if something isn't available, offer support anyway\n\nIf no matching products are found in Zava's catalog, say:\n\"Thanks for sharing those details! I've searched our catalog, but it looks like we don't currently have a product that fits your exact needs. If you'd like, I can suggest some alternatives or help you adjust your project requirements to see if something similar might work.\"",
        mcp_servers = servers,
        model = OpenAIChatCompletionsModel("gpt-5-mini", openaiClient),
        model_settings = ModelSettings(
            reasoning = {
            },
        ),
    )

    try:
        for server in servers:
            await server.connect()
        result = await Runner.run(
            agent,
            [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_image",
                            "detail": "auto",
                            "image_url": encodeImage("/workspace/img/demo-living-room.png", "image/png"),
                        },
                        {
                            "type": "input_text",
                            "text": "Here's a photo of my living room. Based on the lighting and layout, recommend a Zava eggshell paint",
                        },
                    ],
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_image",
                            "detail": "auto",
                            "image_url": encodeImage("/workspace/img/demo-living-room.png", "image/png"),
                        },
                        {
                            "type": "input_text",
                            "text": "Here's a photo of my living room. Based on the lighting and layout, recommend a Zava eggshell paint",
                        },
                    ],
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_image",
                            "detail": "auto",
                            "image_url": encodeImage("/workspace/img/demo-living-room.png", "image/png"),
                        },
                        {
                            "type": "input_text",
                            "text": "Here's a photo of my living room. Based on the lighting and layout, recommend a Zava eggshell paint",
                        },
                    ],
                },
                {
                    "id": "",
                    "type": "message",
                    "role": "assistant",
                    "status": "completed",
                    "content": [
                        {
                            "type": "output_text",
                            "text": "[{\"type\":\"text\",\"text\":\"{\\\"result\\\":\\\"Query Results:\\\\n{\\\\n  \\\\\\\"results\\\\\\\": [\\\\n    {\\\\n      \\\\\\\"product_name\\\\\\\": \\\\\\\"Interior Eggshell Paint\\\\\\\",\\\\n      \\\\\\\"type_name\\\\\\\": \\\\\\\"INTERIOR PAINT\\\\\\\",\\\\n      \\\\\\\"category_name\\\\\\\": \\\\\\\"PAINT & FINISHES\\\\\\\",\\\\n      \\\\\\\"price\\\\\\\": \\\\\\\"65.67\\\\\\\",\\\\n      \\\\\\\"total_stock\\\\\\\": 9093\\\\n    }\\\\n  ],\\\\n  \\\\\\\"row_count\\\\\\\": 1,\\\\n  \\\\\\\"columns\\\\\\\": [\\\\n    \\\\\\\"product_name\\\\\\\",\\\\n    \\\\\\\"type_name\\\\\\\",\\\\n    \\\\\\\"category_name\\\\\\\",\\\\n    \\\\\\\"price\\\\\\\",\\\\n    \\\\\\\"total_stock\\\\\\\"\\\\n  ]\\\\n}\\\"}\"}]",
                            "annotations": [],
                        },
                    ],
                },
                {
                    "id": "",
                    "type": "message",
                    "role": "assistant",
                    "status": "completed",
                    "content": [
                        {
                            "type": "output_text",
                            "text": "Nice — thanks for the photo! Your room has plenty of natural light and warm, neutral furnishings, so a soft, warm eggshell will keep the space cozy while giving walls a subtle, low-sheen glow.\n\nBest Zava pick:\n- Product: Interior Eggshell Paint\n- Why it fits: eggshell finish gives a gentle, non-reflective sheen that keeps the walls feeling soft in bright daylight, is more forgiving of small surface imperfections than flat paint, and is wipeable for living-room use.\n- Practicals: Price £65.67; current stock 9,093.\n\nNext steps — quick questions:\n- Do you prefer a warmer cream (to match the wood/tan tones) or a cooler off-white?\n- Tell me the room dimensions (or wall area) and whether you want 1–2 coats so I can suggest how much paint to buy and whether you’d like a sample pot first.",
                            "annotations": [],
                        },
                    ],
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": "How much is Zava's eggshell paint?",
                        },
                    ],
                },
            ]
        )
        print("")
        print("[Model Response] " + str(result.final_output))
    except Exception as e:
        print(f"\nError: {str(e)}")
    finally:
        for server in servers:
            await server.cleanup()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except asyncio.exceptions.CancelledError:
        # ignore cleanup cancel error
        pass