import requests

# ====== SETUP ======
TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjbGllbnRfaWQiOiJhd3NfaGFja2F0aG9uIiwiZXhwaXJlcyI6MTc0NTc0ODAwMH0.9qpg1xraE_d_Hua2brAmCfRlQSce6p2kdipgq8j1iqo'  # <-- Replace with your real Bearer Token
BASE_URL = 'https://persona-sound.data.gamania.com/api/v1/public/voice'  # use UAT if testing
TEXT = '七連敗怎麼不找找自己的問題？你買不起房，找自己的問題好不好？你結不起婚，也找自己的問題好不好？你買不起車，也找自己的問題好不好？你大學畢業找不到工作，也找你自己的問題好不好？為什麼別人就能欺負你？為什麼就你每天上十幾個小時的班？為什麼你的月收入就只有兩三千塊？全部找自己的問題好不好？為什麼你工作一小時，肉蛋奶米麵蔬菜全都買不起？找自己的問題好不好？什麼都讓你找自己的問題！上不去分也找自己的問題？'  # The text you want to synthesize
MODEL_ID = 2  # Changed from 1 to 2 (max)
SPEED_FACTOR = 1.0  # Speed of the audio
MODE = 'file'  # Return audio file download link
SAVE_PATH = 'output.wav'  # Where to save the audio

# Model ID to Speaker Name mapping
MODEL_TO_SPEAKER = {
    1: 'long',
    2: 'max',
    4: 'chiachi',
    5: 'junting',
    6: 'puyang'
}

# ====== MAKE REQUEST ======
params = {
    'text': TEXT,
    'model_id': MODEL_ID,
    'speaker_name': MODEL_TO_SPEAKER.get(MODEL_ID, 'long'),  # Automatically use speaker name based on model ID
    'speed_factor': SPEED_FACTOR,
    'mode': MODE
}

headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {TOKEN}'
}

response = requests.get(BASE_URL, headers=headers, params=params)

print(f"Status code: {response.status_code}")
print(f"Response: {response.text}")

try:
    if response.status_code == 200:
        data = response.json()
        media_url = data.get('media_url')
        
        if media_url:
            print(f"Downloading audio from {media_url}...")
            audio_response = requests.get(media_url)
            with open(SAVE_PATH, 'wb') as f:
                f.write(audio_response.content)
            print(f"Audio saved to {SAVE_PATH}")
        else:
            print("No media URL returned.")
    else:
        print(f"Failed to call API: {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"Error processing response: {e}")
    print(f"Raw response: {response.text}")
