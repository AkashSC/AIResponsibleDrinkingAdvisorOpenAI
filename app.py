from flask import Flask, request, jsonify, render_template_string
from openai import OpenAI
import os

app = Flask(__name__)

# Initialize OpenAI client (new API)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# HTML template for UI
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Responsible Drinking Advisor</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f9f9f9; }
        .container { max-width: 700px; margin: auto; background: white; padding: 20px; border-radius: 12px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        h2 { color: #2c3e50; }
        label { font-weight: bold; }
        input, textarea, select { width: 100%; padding: 10px; margin: 10px 0; border-radius: 8px; border: 1px solid #ccc; }
        button { background: #2ecc71; color: white; border: none; padding: 12px; border-radius: 8px; cursor: pointer; }
        button:hover { background: #27ae60; }
        .response { margin-top: 20px; padding: 15px; background: #ecf0f1; border-radius: 8px; }
    </style>
</head>
<body>
    <div class="container">
        <h2>🍸 Responsible Drinking Advisor</h2>
        <form method="POST" action="/">
            <label for="question">Ask the AI Advisor:</label>
            <textarea name="question" rows="3"></textarea>

            <label for="drinks">Number of drinks:</label>
            <input type="number" name="drinks" min="0" placeholder="e.g., 3">

            <label for="hours">Hours of drinking:</label>
            <input type="number" name="hours" min="1" placeholder="e.g., 2">

            <label for="weight">Weight (kg):</label>
            <input type="number" name="weight" min="30" max="200" placeholder="e.g., 70">

            <label for="gender">Gender:</label>
            <select name="gender">
                <option value="">--Select--</option>
                <option value="male">Male</option>
                <option value="female">Female</option>
            </select>

            <button type="submit">Get Advice</button>
        </form>

        {% if advice %}
        <div class="response">
            <strong>Advisor says:</strong>
            <p>{{ advice }}</p>
        </div>
        {% endif %}

        {% if hydration %}
        <div class="response">
            <strong>Hydration & BAC Estimate:</strong>
            <p>{{ hydration }}</p>
        </div>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def home():
    advice = None
    hydration = None

    if request.method == "POST":
        user_question = request.form.get("question", "")
        drinks = request.form.get("drinks")
        hours = request.form.get("hours")
        weight = request.form.get("weight")
        gender = request.form.get("gender")

        # --- AI Advisor ---
        if user_question:
            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": 
                         "You are a Responsible Drinking Advisor. "
                         "Encourage moderation, hydration, and safe behavior. "
                         "Never promote binge drinking or unsafe alcohol use. "
                         "Provide tips about responsible drinking, local laws, and health."},
                        {"role": "user", "content": user_question}
                    ]
                )
                advice = response.choices[0].message.content
            except Exception as e:
                advice = f"Error: {str(e)}"

        # --- BAC-lite Calculator ---
        if drinks and hours and weight and gender:
            try:
                drinks = int(drinks)
                hours = int(hours)
                weight = float(weight)
                r = 0.73 if gender == "male" else 0.66

                # Convert kg to lbs
                weight_lbs = weight * 2.20462

                # Widmark BAC formula
                bac = (drinks * 14 * 5.14) / (weight_lbs * r) - 0.015 * hours
                bac = max(bac, 0)

                # Categorize BAC
                if bac < 0.03:
                    status = "Minimal impairment."
                elif bac < 0.06:
                    status = "Mild impairment. You may feel relaxed but should still be cautious."
                elif bac < 0.08:
                    status = "Legally impaired in many countries. Driving is unsafe."
                else:
                    status = "Dangerous level. Do NOT drive and consider stopping immediately."

                hydration = f"Estimated BAC: {bac:.3f}. {status} Always hydrate with water between drinks."

            except Exception as e:
                hydration = f"Error in calculation: {str(e)}"

    return render_template_string(HTML_PAGE, advice=advice, hydration=hydration)


@app.route("/advisor", methods=["POST"])
def advisor():
    """API endpoint for JSON access"""
    data = request.get_json(silent=True) or {}
    user_question = data.get("question", "")

    if not user_question:
        return jsonify({"error": "No question provided"}), 400

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": 
                 "You are a Responsible Drinking Advisor. "
                 "Encourage moderation, hydration, and safe behavior. "
                 "Never promote binge drinking or unsafe alcohol use. "
                 "Provide tips about responsible drinking, local laws, and health."},
                {"role": "user", "content": user_question}
            ]
        )
        return jsonify({"advice": response.choices[0].message.content})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
