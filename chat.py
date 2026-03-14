import os
from flask import Blueprint, request, jsonify
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

chat_bp = Blueprint("chat", __name__)

# Create OpenAI client (NVIDIA-compatible)
client = OpenAI(
    base_url=os.getenv("NVIDIA_BASE_URL"),
    api_key=os.getenv("NVIDIA_API_KEY")
)

@chat_bp.route("/api/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        user_message = data.get("message", "").strip()

        if not user_message:
            return jsonify({"reply": "Please ask a valid question."}), 400

        # ---- GPT-OSS Streaming Call ----
        completion = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are Cricket Coach Pro AI. "
                        "Give short, actionable cricket insights. "
                        "If data is missing, say 'Not enough data'."
                    )
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ],
            temperature=0.6,
            top_p=1,
            max_tokens=512,
            stream=True
        )

        final_reply = ""

        for chunk in completion:
            delta = chunk.choices[0].delta

            # Optional: reasoning tokens (GPT-OSS feature)
            reasoning = getattr(delta, "reasoning_content", None)
            if reasoning:
                # We do NOT send reasoning to frontend
                pass

            if delta.content:
                final_reply += delta.content

        return jsonify({"reply": final_reply.strip()})

    except Exception as e:
        print("CHAT ERROR:", str(e))
        return jsonify({
            "reply": "AI service failed. Please try again later."
        }), 500
