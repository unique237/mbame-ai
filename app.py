from flask import Flask, render_template, request, session
from dotenv import load_dotenv
import os
import requests
import json
import markdown2

# Initialize Flask app
app = Flask(__name__)

# Set a secret key for session management (required for sessions)
app.secret_key = os.getenv(
    "FLASK_SECRET_KEY", "your-secret-key-here"
)  # Fallback if not set in .env

# Load environment variables from .env file
load_dotenv()
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")


# Route for the homepage
@app.route("/")
def index():
    # Initialize session history if not present
    if "conversation_history" not in session:
        session["conversation_history"] = []
    return render_template(
        "index.html", conversation_history=session["conversation_history"]
    )


# Route to handle form submission and DeepSeek API call
@app.route("/ask", methods=["POST"])
def ask():
    user_input = request.form.get("user_input")
    if not user_input:
        if "conversation_history" not in session:
            session["conversation_history"] = []
        return render_template(
            "index.html",
            response="Please enter a question.",
            user_input="",
            conversation_history=session["conversation_history"],
        )

    # DeepSeek API call
    try:
        url = "https://api.deepseek.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "system",
                    "content": "You are Mbame-AI, a helpful and general-purpose conversational AI. Provide concise and accurate answers to user questions.",
                },
                {"role": "user", "content": user_input},
            ],
            "max_tokens": 500,
            "temperature": 0.7,
        }
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Raise exception for bad status codes

        # Extract the AI's response
        api_response = response.json()
        answer = api_response["choices"][0]["message"]["content"]

        # Format the response with markdown
        answer = api_response["choices"][0]["message"]["content"]
        formatted_answer = markdown2.markdown(answer)

        # Append to session's conversation history
        if "conversation_history" not in session:
            session["conversation_history"] = []
        session["conversation_history"].append(
            {"user": user_input, "ai": formatted_answer}
        )
        session.modified = True

        return render_template(
            "index.html",
            response=formatted_answer,
            user_input=user_input,
            conversation_history=session["conversation_history"],
        )
    except requests.exceptions.RequestException as e:
        error_message = f"Error communicating with DeepSeek API: {str(e)}"
        if "conversation_history" not in session:
            session["conversation_history"] = []
        session["conversation_history"].append(
            {"user": user_input, "ai": error_message}
        )
        session.modified = True
        return render_template(
            "index.html",
            response=error_message,
            user_input=user_input,
            conversation_history=session["conversation_history"],
        )
    except KeyError:
        error_message = "Error: Invalid response format from DeepSeek API."
        if "conversation_history" not in session:
            session["conversation_history"] = []
        session["conversation_history"].append(
            {"user": user_input, "ai": error_message}
        )
        session.modified = True
        return render_template(
            "index.html",
            response=error_message,
            user_input=user_input,
            conversation_history=session["conversation_history"],
        )
    except Exception as e:
        error_message = f"Unexpected error: {str(e)}"
        if "conversation_history" not in session:
            session["conversation_history"] = []
        session["conversation_history"].append(
            {"user": user_input, "ai": error_message}
        )
        session.modified = True
        return render_template(
            "index.html",
            response=error_message,
            user_input=user_input,
            conversation_history=session["conversation_history"],
        )


if __name__ == "__main__":
    import os

    port = int(os.environ.get("PORT", 5000))  # Required for Render
    app.run(host="0.0.0.0", port=port, debug=False)
