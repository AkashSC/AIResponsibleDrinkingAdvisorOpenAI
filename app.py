from flask import Flask, request, jsonify, render_template_string
from utils.openai_helper import get_ai_response

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        user_input = request.form.get("prompt")
        ai_output = get_ai_response(user_input)
        return render_template_string("""
            <h2>AI Response</h2>
            <p><b>You:</b> {{ user_input }}</p>
            <p><b>AI:</b> {{ ai_output }}</p>
            <a href="/">Go Back</a>
        """, user_input=user_input, ai_output=ai_output)
    return '''
        <form method="POST">
            <input type="text" name="prompt" placeholder="Ask me anything" required>
            <button type="submit">Submit</button>
        </form>
    '''

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
