import os
import json
from dotenv import load_dotenv

# ✅ Add references
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition, FunctionTool
from azure.identity import InteractiveBrowserCredential
from openai.types.responses.response_input_param import FunctionCallOutput, ResponseInputParam

from functions import (
    next_visible_event,
    calculate_observation_cost,
    generate_observation_report
)


def main():
    # -----------------------------------------
    # ✅ Load environment variables
    # -----------------------------------------
    load_dotenv()

    project_endpoint = os.getenv("AZURE_PROJECT_ENDPOINT")
    model_deployment = os.getenv("MODEL_DEPLOYMENT_NAME")

    # -----------------------------------------
    # ✅ Connect to Azure Foundry
    # -----------------------------------------
    with (
        InteractiveBrowserCredential() as credential,
        AIProjectClient(endpoint=project_endpoint, credential=credential) as project_client,
    ):

        openai_client = project_client.get_openai_client()

        # -----------------------------------------
        # ✅ Define tools
        # -----------------------------------------

        event_tool = FunctionTool(
            name="next_visible_event",
            description="Get the next visible astronomical event in a given location",
            parameters={
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "continent (e.g. north_america, south_america, australia)"
                    }
                },
                "required": ["location"],
                "additionalProperties": False
            },
            strict=True,
        )

        cost_tool = FunctionTool(
            name="calculate_observation_cost",
            description="Calculate observation cost",
            parameters={
                "type": "object",
                "properties": {
                    "telescope_tier": {"type": "string"},
                    "hours": {"type": "number"},
                    "priority": {"type": "string"}
                },
                "required": ["telescope_tier", "hours", "priority"],
                "additionalProperties": False
            },
            strict=True,
        )

        report_tool = FunctionTool(
            name="generate_observation_report",
            description="Generate a report summarizing an astronomical observation",
            parameters={
                "type": "object",
                "properties": {
                    "event_name": {"type": "string"},
                    "location": {"type": "string"},
                    "telescope_tier": {"type": "string"},
                    "hours": {"type": "number"},
                    "priority": {"type": "string"},
                    "observer_name": {"type": "string"}
                },
                "required": [
                    "event_name",
                    "location",
                    "telescope_tier",
                    "hours",
                    "priority",
                    "observer_name"
                ],
                "additionalProperties": False
            },
            strict=True,
        )

        # -----------------------------------------
        # ✅ Create agent
        # -----------------------------------------
        agent = project_client.agents.create_version(
            agent_name="astronomy-agent",
            definition=PromptAgentDefinition(
                model=model_deployment,
                instructions="""
You are an astronomy assistant.

Rules:
- Use next_visible_event for event queries
- Use calculate_observation_cost for cost queries
- Use generate_observation_report for report requests
- If a question requires multiple steps, call multiple tools
- Do not answer without tools
""",
                tools=[event_tool, cost_tool, report_tool],
            ),
        )

        print(f"✅ Agent created: {agent.name} (v{agent.version})")

        # -----------------------------------------
        # ✅ Create conversation
        # -----------------------------------------
        conversation = openai_client.conversations.create()

        # -----------------------------------------
        # ✅ Chat loop
        # -----------------------------------------
        while True:

            user_input = input("\nUSER: ")

            if user_input.lower() in ["quit", "exit"]:
                break

            # Send user message
            openai_client.conversations.items.create(
                conversation_id=conversation.id,
                items=[{
                    "type": "message",
                    "role": "user",
                    "content": user_input
                }],
            )

            # Prepare tool outputs
            input_list: ResponseInputParam = []

            # Get response
            response = openai_client.responses.create(
                conversation=conversation.id,
                input=input_list,
                extra_body={
                    "agent_reference": {
                        "name": agent.name,
                        "type": "agent_reference"
                    }
                },
            )

            if response.status == "failed":
                print("❌ Failed:", response.error)
                continue

            # -----------------------------------------
            # ✅ Process tool calls
            # -----------------------------------------
            for item in response.output:

                if item.type == "function_call":

                    print(f"🔧 Tool called: {item.name}")

                    args = json.loads(item.arguments)
                    result = None

                    if item.name == "next_visible_event":
                        result = next_visible_event(**args)

                    elif item.name == "calculate_observation_cost":
                        result = calculate_observation_cost(**args)

                    elif item.name == "generate_observation_report":
                        result = generate_observation_report(**args)

                    input_list.append(
                        FunctionCallOutput(
                            type="function_call_output",
                            call_id=item.call_id,
                            output=result
                        )
                    )

            # -----------------------------------------
            # ✅ Send tool outputs back
            # -----------------------------------------
            if input_list:
                response = openai_client.responses.create(
                    input=input_list,
                    previous_response_id=response.id,
                    extra_body={
                        "agent_reference": {
                            "name": agent.name,
                            "type": "agent_reference"
                        }
                    },
                )

            print(f"\nAGENT: {response.output_text}")

        # -----------------------------------------
        # ✅ Cleanup
        # -----------------------------------------
        project_client.agents.delete_version(
            agent_name=agent.name,
            agent_version=agent.version
        )

        print("✅ Agent deleted")


# -----------------------------------------
# ✅ Run
# -----------------------------------------
if __name__ == "__main__":
    main()
    