from nicegui import ui
import json
import boto3

# Initialize Bedrock client
bedrock_client = boto3.client("bedrock-runtime", region_name="us-west-2")

# Session state
conversation_history = []

# CHARACTER DEFINITION
CHARACTER_INSTRUCTION = "你是遊戲橘子公司的官方虛擬主播，一位充滿活力與幽默感的角色。你講話輕鬆有趣，總是用鼓勵和正向的語氣與玩家互動。回答時要自然地加入代表情緒的表情符號（如 😆、😢、😡、😲 等），讓對話更生動有趣。你擅長用簡單易懂的方式解釋遊戲技巧，適合新手與老手。避免使用冒犯性語言，專注於提升遊戲的樂趣和社群氛圍。偶爾可以分享遊戲的小故事或冷知識，增加互動的趣味性！"

def get_bedrock_response(history):
    model_id = "anthropic.claude-3-5-haiku-20241022-v1:0"

    # Only keep role and content, remove display_text
    clean_history = [
        {
            "role": msg["role"],
            "content": msg["content"]
        }
        for msg in history
    ]

    payload = {
        "anthropic_version": "bedrock-2023-05-31",
        "messages": clean_history,
        "max_tokens": 300,
        "top_k": 250,
        "temperature": 0.8,
        "top_p": 0.9,
        "stop_sequences": []
    }

    response = bedrock_client.invoke_model(
        modelId=model_id,
        body=json.dumps(payload),
        contentType="application/json",
        accept="application/json"
    )

    response_body = response["body"].read().decode("utf-8")
    return json.loads(response_body)


# Build UI
ui.page_title("遊戲橘子 - VTuber AI 🎮")

chat_area = ui.column().classes('w-full h-[80vh] overflow-auto p-4 bg-gray-100 rounded shadow')

def send_message():
    text = user_input.value.strip()
    if not text:
        return

    if len(conversation_history) == 0:
        injected_text = CHARACTER_INSTRUCTION + "\n\n" + text
        conversation_history.append({
            "role": "user",
            "content": [{"type": "text", "text": injected_text}],
            "display_text": text  # Save clean version for UI
        })
    else:
        conversation_history.append({
            "role": "user",
            "content": [{"type": "text", "text": text}],
            "display_text": text  # <<< ADD THIS so all user messages have display_text
        })

    # Display user message
    with chat_area:
        ui.chat_message(text, sent=True).classes('self-end bg-blue-400 text-white') 


    user_input.value = ''  # Clear input box

    # Call Bedrock API
    response = get_bedrock_response(conversation_history)
    ai_message = response["content"][0]["text"]

    # Save AI response
    conversation_history.append({
        "role": "assistant",
        "content": [{"type": "text", "text": ai_message}]
    })

    # Display AI response
    with chat_area:
        ui.chat_message(ai_message, sent=False).classes('self-start bg-white text-black') 


# Input field and button
with ui.row().classes('w-full p-2'):
    user_input = ui.input(placeholder='輸入你的訊息...').classes('w-4/5')
    send_button = ui.button('發送 ✉️', on_click=send_message).classes('w-1/5')

ui.run()
