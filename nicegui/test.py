import json
import boto3
import uuid

# Your agent info
AGENT_ID = "04SYMPXB10"
AGENT_ALIAS_ID = "LOOJMCRBV9"
SESSION_ID = str(uuid.uuid4())  # Same session id for continuous chat

bedrock_agent_client = boto3.client("bedrock-agent-runtime", region_name="us-west-2")


def send_to_agent(user_input_text):
    try:
        response_stream = bedrock_agent_client.invoke_agent(
            agentId=AGENT_ID,
            agentAliasId=AGENT_ALIAS_ID,
            sessionId=SESSION_ID,
            inputText=user_input_text
        )

        full_response = []

        for event in response_stream["completion"]:
            if "chunk" in event:
                chunk_text = event["chunk"]["bytes"].decode("utf-8")
                full_response.append(chunk_text)

        return "".join(full_response)

    except Exception as e:
        print(f"Error invoking agent: {e}")
        return "出錯了，請稍後再試！"


def main():
    print("開始聊天！輸入 'exit' 離開。")
    while True:
        user_message = input("\n你：")
        if user_message.lower() in ['exit', 'quit', 'bye']:
            print("結束對話，再見！👋")
            break

        agent_reply = send_to_agent(user_message)
        print(f"\n助理：{agent_reply}")


if __name__ == "__main__":
    main()
