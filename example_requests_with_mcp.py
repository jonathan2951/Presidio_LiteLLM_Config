import requests
import json


def parse_sse_response(sse_text):
    """Parse Server-Sent Events (SSE) response and extract JSON data"""
    lines = sse_text.strip().split('\n')

    for line in lines:
        if line.startswith('data: '):
            # Extract JSON data after "data: " prefix
            json_str = line[6:]  # Skip "data: " (6 characters)
            try:
                return json.loads(json_str)
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON from SSE data line: {e}")
                print(f"JSON string: {json_str[:200]}")
                return None

    print("No 'data:' line found in SSE response")
    return None


def get_mcp_tools(mcp_server_url):
    """Fetch tools from MCP server and convert to OpenAI function format"""
    print(f"\nFetching tools from MCP server: {mcp_server_url}")

    try:
        # MCP protocol: list available tools
        response = requests.post(
            mcp_server_url,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream"
            },
            json={
                "jsonrpc": "2.0",
                "method": "tools/list",
                "params": {},
                "id": 1
            },
            timeout=10
        )
        response.raise_for_status()

        # Parse SSE response (Server-Sent Events)
        if 'text/event-stream' in response.headers.get('content-type', ''):
            print(f"Parsing SSE response...")
            mcp_data = parse_sse_response(response.text)
            if mcp_data is None:
                print("Failed to parse SSE response")
                return []
        else:
            # Fall back to regular JSON parsing
            mcp_data = response.json()

        print(f"Parsed MCP response successfully\n")

        # Convert MCP tools to OpenAI function calling format
        tools = []
        mcp_tools = mcp_data.get("result", {}).get("tools", [])

        print(f"Found {len(mcp_tools)} tools from MCP server")

        for tool in mcp_tools:
            openai_tool = {
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool.get("description", ""),
                    "parameters": tool.get("inputSchema", {
                        "type": "object",
                        "properties": {},
                        "required": []
                    })
                }
            }
            tools.append(openai_tool)
            print(f"  - {tool['name']}: {tool.get('description', 'No description')[:60]}...")

        return tools

    except requests.exceptions.RequestException as e:
        print(f"Error fetching MCP tools (RequestException): {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response status: {e.response.status_code}")
            print(f"Response text: {e.response.text}")
        return []
    except ValueError as e:
        print(f"Error parsing MCP response (ValueError): {e}")
        print(f"This usually means the server returned non-JSON content")
        return []
    except Exception as e:
        print(f"Unexpected error: {type(e).__name__}: {e}")
        return []


def execute_mcp_tool(mcp_server_url, tool_name, arguments):
    """Execute a tool call on the MCP server"""
    print(f"\nExecuting MCP tool: {tool_name}")
    print(f"Arguments: {arguments}")

    try:
        response = requests.post(
            mcp_server_url,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream"
            },
            json={
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments
                },
                "id": 2
            },
            timeout=30
        )
        response.raise_for_status()

        # Parse SSE response (Server-Sent Events)
        if 'text/event-stream' in response.headers.get('content-type', ''):
            result = parse_sse_response(response.text)
            if result is None:
                print("Failed to parse SSE response from tool execution")
                return None
        else:
            # Fall back to regular JSON parsing
            result = response.json()

        print(f"Tool execution result: {result}")
        return result

    except requests.exceptions.RequestException as e:
        print(f"Error executing MCP tool: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
        return None


def test_litellm():
    """Test LiteLLM proxy with presidio guardrails and MCP tools"""
    print("\n" + "=" * 80)
    print("3. TESTING LITELLM WITH PRESIDIO GUARDRAILS + MCP TOOLS")
    print("=" * 80)

    # Fetch and convert MCP tools to OpenAI format
    mcp_server_url = "" # add MCP server URL
    tools = get_mcp_tools(mcp_server_url)

    text = """use the databricks_get_categorical_col_statistisc tool on:
    - catalog: psfa-demo
    - schema: silver
    - table: supply_chain
    - column: supplier_name"""

    print(f"\nPrompt: {text}\n")

    try:
        # Build the request payload
        payload = {
            "model": "gpt-4o",
            "messages": [{"role": "user", "content": text}]
        }

        # Add tools if we successfully fetched them
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"
            print(f"Sending request with {len(tools)} tools available\n")
        else:
            print("No MCP tools available, sending request without tools\n")

        response = requests.post(
            "http://localhost:4000/v1/chat/completions",
            headers={"Authorization": "Bearer sk-1234"},
            json=payload
        )
        response.raise_for_status()
        result = response.json()

        print(f"Status: {response.status_code}")
        print(f"\nLLM Response:")

        message = result['choices'][0]['message']

        # Check if the model wants to call a tool
        if 'tool_calls' in message and message['tool_calls']:
            print(f"  Model requested tool calls:")
            for tool_call in message['tool_calls']:
                print(f"    - Tool: {tool_call['function']['name']}")
                print(f"      Arguments: {tool_call['function']['arguments']}")
        else:
            print(f"  {message.get('content', 'No content')}")

        print(f"\nModel used: {result.get('model', 'N/A')}")
        print(f"Tokens: {result.get('usage', {})}")

        return result
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
        return None


def test_litellm_with_tool_execution():
    """Complete workflow: LiteLLM -> Tool Call -> MCP Execution"""
    print("\n" + "=" * 80)
    print("4. COMPLETE WORKFLOW: LITELLM + MCP TOOL EXECUTION")
    print("=" * 80)

    mcp_server_url = "" # add MCP server URL
    tools = get_mcp_tools(mcp_server_url)

    if not tools:
        print("No tools available, skipping complete workflow test")
        return None

    # text = """use the databricks_get_categorical_col_statistics tool on:
    # - catalog: psfa-demo
    # - schema: silver
    # - table: supply_chain
    # - column: supplier_name"""
    text = """use the databricks_get_numerical_col_statistics tool on:
    - catalog: psfa-demo
    - schema: silver
    - table: budget
    - column: total_budget"""

    print(f"\nPrompt: {text}\n")

    messages = [{"role": "user", "content": text}]

    try:
        # Step 1: Initial LLM call with tools
        response = requests.post(
            "http://localhost:4000/v1/chat/completions",
            headers={"Authorization": "Bearer sk-1234"},
            json={
                "model": "gpt-4o",
                "messages": messages,
                "tools": tools,
                "tool_choice": "auto"
            }
        )
        response.raise_for_status()
        result = response.json()

        message = result['choices'][0]['message']
        print(f"LLM Response received (finish_reason: {result['choices'][0].get('finish_reason')})")

        # Step 2: Check if tool calls were requested
        if 'tool_calls' in message and message['tool_calls']:
            print(f"\n{len(message['tool_calls'])} tool call(s) requested:")

            # Add assistant message to conversation
            messages.append(message)

            # Execute each tool call
            for tool_call in message['tool_calls']:
                tool_name = tool_call['function']['name']
                import json
                arguments = json.loads(tool_call['function']['arguments'])

                print(f"\n  Executing: {tool_name}")
                print(f"  Arguments: {arguments}")

                # Execute on MCP server
                tool_result = execute_mcp_tool(mcp_server_url, tool_name, arguments)

                if tool_result:
                    # Add tool result to conversation
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call['id'],
                        "content": json.dumps(tool_result.get("result", {}))
                    })

            # Step 3: Send tool results back to LLM for final response
            print("\n" + "-" * 80)
            print("Sending tool results back to LLM...")
            print("-" * 80)

            final_response = requests.post(
                "http://localhost:4000/v1/chat/completions",
                headers={"Authorization": "Bearer sk-1234"},
                json={
                    "model": "gpt-4o",
                    "messages": messages
                }
            )
            final_response.raise_for_status()
            final_result = final_response.json()

            print(f"\nFinal LLM Response:")
            print(f"  {final_result['choices'][0]['message']['content']}")
            print(f"\nTotal tokens used: {final_result.get('usage', {})}")

            return final_result
        else:
            print(f"\nNo tool calls requested. Response:")
            print(f"  {message.get('content', 'No content')}")
            return result

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
        return None


if __name__ == "__main__":

    # # Test 3: LiteLLM with tools (no execution)
    # test_litellm()

    # Test 4: Complete workflow with tool execution
    test_litellm_with_tool_execution()

    print("\n" + "=" * 80)
    print("TESTS COMPLETE")
    print("=" * 80)
