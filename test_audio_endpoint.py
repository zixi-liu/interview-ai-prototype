"""
Test audio endpoint with a sample audio
"""
import requests
import base64

# Create a simple test by calling the endpoint
def test_audio_endpoint():
    url = "http://127.0.0.1:5000/analyze/audio"

    # Test data
    data = {
        "role": "Software Engineer",
        "company": "Google"
    }

    # We need actual audio file to test
    # Let's first test if the endpoint is reachable
    print("Testing audio endpoint...")

    # Check if we have a sample audio file
    import os
    if not os.path.exists("sample_audio.webm"):
        print("❌ No sample audio file found. Please record audio through the UI first.")
        return

    with open("sample_audio.webm", "rb") as audio_file:
        files = {"audio": ("recording.webm", audio_file, "audio/webm")}

        print(f"Sending request to {url}")
        print(f"Data: {data}")

        response = requests.post(url, data=data, files=files)

        print(f"\nResponse status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("✅ Success!")
            print(f"\nTranscription: {result.get('transcription', 'N/A')}")
            print(f"\nFeedback:\n{result.get('feedback', 'N/A')}")
            print(f"\nModel: {result.get('model', 'N/A')}")
        else:
            print(f"❌ Error: {response.text}")

if __name__ == "__main__":
    test_audio_endpoint()
