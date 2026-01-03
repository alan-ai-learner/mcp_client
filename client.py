# import asyncio
# from langchain_mcp_adapters.client import MultiServerMCPClient
# from dotenv import load_dotenv
# from langchain_openai import ChatOpenAI
# from langchain_core.messages import ToolMessage
# import json

# load_dotenv()

# SERVERS = { 
#     # "math": {
#     #     "transport": "stdio",
#     #     "command": "/Library/Frameworks/Python.framework/Versions/3.11/bin/uv",
#     #     "args": [
#     #         "run",
#     #         "fastmcp",
#     #         "run",
#     #         "/Users/nitish/Desktop/mcp-math-server/main.py"
#     #    ]
#     # },
#     "expense": {
#         "transport": "streamable_http",  # if this fails, try "sse"
#         "url": "https://rural-aqua-walrus.fastmcp.app/mcp"
#     },
#     "manim-server": {
#         "transport": "stdio",
#         "command": "/Library/Frameworks/Python.framework/Versions/3.11/bin/python3",
#         "args": [
#         "/Users/nitish/desktop/manim-mcp-server/src/manim_server.py"
#       ],
#         "env": {
#         "MANIM_EXECUTABLE": "/Library/Frameworks/Python.framework/Versions/3.11/bin/manim"
#       }
#     }
# }

# async def main():
    
#     client = MultiServerMCPClient(SERVERS)
#     tools = await client.get_tools()


#     named_tools = {}
#     for tool in tools:
#         named_tools[tool.name] = tool

#     print("Available tools:", named_tools.keys())

#     llm = ChatOpenAI(model="gpt-5")
#     llm_with_tools = llm.bind_tools(tools)

#     prompt = "Draw a triangle rotating in place using the manim tool."
#     response = await llm_with_tools.ainvoke(prompt)

#     if not getattr(response, "tool_calls", None):
#         print("\nLLM Reply:", response.content)
#         return

#     tool_messages = []
#     for tc in response.tool_calls:
#         selected_tool = tc["name"]
#         selected_tool_args = tc.get("args") or {}
#         selected_tool_id = tc["id"]

#         result = await named_tools[selected_tool].ainvoke(selected_tool_args)
#         tool_messages.append(ToolMessage(tool_call_id=selected_tool_id, content=json.dumps(result)))
        

#     final_response = await llm_with_tools.ainvoke([prompt, response, *tool_messages])
#     print(f"Final response: {final_response.content}")


# if __name__ == '__main__':
#     asyncio.run(main())


import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import ToolMessage
import json
import os

load_dotenv()

# SERVERS = { 
#     "expense": {
#         "transport": "streamable_http",
#         "url": "https://rural-aqua-walrus.fastmcp.app/mcp"},
    
#     "math-server": {
#         "transport": "stdio",
#         "command": "C:/Users/alank/AppData/Local/Programs/Python/Python312/Scripts/uv",
#         "args": [
#             "run",
#             "fastmcp",  
#             "run",
#             "D:/mcp_servers/mcp_math_server/main.py"
#         ],
#     }
# }
import sys  # <--- Add this import at the top

# ... inside your SERVERS dictionary ...

SERVERS = { 
    "expense": {
        "transport": "streamable_http",
        "url": "https://usage-check.fastmcp.app/mcp"
    },
    
    # "math-server": {
    #     "transport": "stdio",
    #     "command": sys.executable, # Uses the current running Python
    #     "args": [
    #         "D:/mcp_servers/mcp_math_server/main.py"
    #     ],
    #     "env": { "LOG_LEVEL": "ERROR" } # Keep this to silence FastMCP logs
    # },

    # "calculator": {
    #     "transport": "stdio",
    #     "command": sys.executable, # Uses the current running Python
    #     "args": [
    #         "D:/mcp_servers/mcp_calculator/calc_server.py"
    #     ],
    #     "env": { "LOG_LEVEL": "ERROR" }
    # }
}

async def main():

    # Connect MCP servers
    client = MultiServerMCPClient(SERVERS)
    tools = await client.get_tools()

    named_tools = {tool.name: tool for tool in tools}
    print("Available tools:", named_tools.keys())

    # ---- USE GEMINI INSTEAD OF CHATGPT ----
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite",
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )

    llm_with_tools = llm.bind_tools(tools)

    prompt = "How much memory is getting used now?"
    response = await llm_with_tools.ainvoke(prompt)

    print(response)
    # If no tool call → just answer normally
    if not getattr(response, "tool_calls", None):
        print("\nLLM Reply:", response.content)
        return

    # Execute tool calls
    tool_messages = []
    for tc in response.tool_calls:
        selected_tool = tc["name"]
        selected_tool_args = tc.get("args") or {}
        selected_tool_id = tc["id"]

        result = await named_tools[selected_tool].ainvoke(selected_tool_args)

        tool_messages.append(
            ToolMessage(tool_call_id=selected_tool_id, content=json.dumps(result))
        )

    # Final Gemini response after tool execution
    final_response = await llm_with_tools.ainvoke(
        [prompt, response, *tool_messages]
    )
    
    print("Final response:", final_response)


if __name__ == '__main__':
    asyncio.run(main())
