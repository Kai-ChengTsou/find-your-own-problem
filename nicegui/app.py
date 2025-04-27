from nicegui import ui, app
import json
import boto3
import uuid
import tempfile
import os

app.add_static_files('/static', '/app/static')

# Initialize Bedrock Agent Runtime client
bedrock_agent_client = boto3.client("bedrock-agent-runtime", region_name="us-west-2")
polly_client = boto3.client('polly', region_name='us-west-2')
# Session state
conversation_history = []

# Your agent info
AGENT_ID = "04SYMPXB10"  # your agent id
AGENT_ALIAS_ID = "LOOJMCRBV9"
SESSION_ID = str(uuid.uuid4())

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

def synthesize_speech(text, voice_id='Zhiyu'):
    try:
        # Call Amazon Polly to generate speech
        response = polly_client.synthesize_speech(
            Text=text,
            VoiceId=voice_id,  # Choose voice ID like 'Zhiyu' (a young-sounding Chinese voice)
            OutputFormat='mp3',
            LanguageCode='cmn-CN'  # Mandarin Chinese
        )

        # Store the audio in a temporary file
        temp_audio_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
        with open(temp_audio_file.name, 'wb') as audio_file:
            audio_file.write(response['AudioStream'].read())

        return temp_audio_file.name  # Return path to audio file

    except Exception as e:
        print(f"Error synthesizing speech: {e}")
        return None


# Full page row
with ui.row().classes('w-full h-full'):

    # LEFT: Avatar (1/3 width)
    with ui.column().classes('w-1/3 items-center justify-center'):
        # Add the canvas container
        ui.html('''
        <div id="live2d-container" style="position:relative;width:300px;height:400px;">
            <canvas id="live2d" width="300" height="400"></canvas>
        </div>
        ''')

        # Load Live2D script
        ui.add_body_html('''
        <script src="https://cdn.jsdelivr.net/gh/stevenjoezhang/live2d-widget@latest/live2d.min.js"></script>
        <script>
        window.addEventListener("load", () => {
            loadlive2d(
                "live2d",
                "https://cdn.jsdelivr.net/gh/evrstr/live2d-widget-models/live2d_evrstr/haru_seifuku/model.json",
                null
            );
        });
        </script>
        ''')

    # RIGHT: Chat (1/2 width)
    with ui.column().classes('w-1/2 h-full p-4 bg-gray-100 rounded shadow overflow-auto'):
        chat_area = ui.column().classes('w-full h-full')

ui.add_css('body { background-color: #f4f4f4; }')

def send_message():
    text = user_input.value.strip()
    if not text:
        return

    # Save user message
    conversation_history.append({
        "role": "user",
        "content": text
    })

    # Display user message
    with chat_area:
        ui.chat_message(text, sent=True).classes('self-end bg-blue-400 text-white') 

    user_input.value = ''  # Clear input box

    # Call Bedrock Agent API
    ai_message = send_to_agent(text)

    # Save AI response
    conversation_history.append({
        "role": "assistant",
        "content": ai_message
    })

    # Display AI response
    with chat_area:
        ui.chat_message(ai_message, sent=False).classes('self-start bg-white text-black') 

    # Synthesize speech using Amazon Polly
    audio_file = synthesize_speech(ai_message, voice_id='Zhiyu')  # 'Zhiyu' is a young Chinese female voice

    # If audio was generated, send it to the frontend to be played
    if audio_file:
        ui.add_body_html(f'''
        <audio id="ai-speech" controls autoplay>
            <source src="/static/{os.path.basename(audio_file)}" type="audio/mp3">
            Your browser does not support the audio element.
        </audio>
        ''')

        # Move the generated file to the static folder
        os.rename(audio_file, f"/app/static/{os.path.basename(audio_file)}")

        
# Input field and button
with ui.row().classes('w-full p-2'):
    user_input = ui.input(placeholder='輸入你的訊息...').classes('w-4/5')
    send_button = ui.button('發送 ✉️', on_click=send_message).classes('w-1/5')

ui.run()
