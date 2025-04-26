from backend.chatbot_core.logic import run_conversation

if __name__ == "__main__":
    image_url = input("이미지 URL을 입력하세요: ").strip().strip('"')
    run_conversation(image_url)