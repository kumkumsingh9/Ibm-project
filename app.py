from flask import Flask, request, jsonify, render_template
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

app = Flask(__name__)

os.environ["GOOGLE_API_KEY"] = "AIzaSyD2A02vLqdn_hjRisViXQptPeOp2HR5InY" 

# Initialize Gemini model
llm = ChatGoogleGenerativeAI(
    model="models/gemini-1.5-flash-latest",
    temperature=0.3
)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/check', methods=['POST'])
def check_sustainability():
    data = request.json
    product = data.get("product", "").strip()

    prompt = f"""
    You are an expert in environmental sustainability.
    Analyze the product: '{product}'

    1. Classify it clearly as either 'Sustainable' or 'Not Sustainable'.
    2. If it's Sustainable, suggest 2-3 items commonly made from it.
       If it's Not Sustainable, suggest 2-3 environmentally-friendly alternatives.
    3. Give 1 short eco-friendly tip for users (can include ways to reduce waste or recycle).
    4. If possible, suggest how to recycle or repurpose this product or its alternatives.

    Respond ONLY in this format:
    Sustainability: Sustainable / Not Sustainable
    Suggestions/Alternatives: <list>
    Tip: <eco tip>
    Recycle/Repurpose: <how to recycle or reuse>
    """

    try:
        # Send prompt to Gemini
        response = llm.invoke([HumanMessage(content=prompt)])
        answer = response.content.strip()

        # Extract structured fields
        lines = answer.split("\n")
        sustainability = suggestion = tip = recycle = ""

        for line in lines:
            if line.lower().startswith("sustainability"):
                sustainability = line.split(":", 1)[1].strip()
            elif line.lower().startswith("suggestions") or line.lower().startswith("alternatives"):
                suggestion = line.split(":", 1)[1].strip()
            elif line.lower().startswith("tip"):
                tip = line.split(":", 1)[1].strip()
            elif line.lower().startswith("recycle") or line.lower().startswith("repurpose"):
                recycle = line.split(":", 1)[1].strip()

        is_sustainable = "sustainable" in sustainability.lower() and "not" not in sustainability.lower()

        msg = (
            f"✅ Yess! {product} is sustainable 🌍🌱🤝🎯"
            if is_sustainable else
            f"❌ Noo! {product} is not sustainable 🚫"
        )

        return jsonify({
            "product": product,
            "sustainable": is_sustainable,
            "message": msg,
            "suggestion_or_alternative": suggestion,
            "tip": tip,
            "recycle": recycle
        })

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

