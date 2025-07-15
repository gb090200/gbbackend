
from flask import Flask, request
from flask_cors import CORS
import smtplib
from email.message import EmailMessage
import os

app = Flask(__name__)
CORS(app)

COURSE_MAP = {
    "powerbi": "Power_BI_Course.pdf",
    "genai": "Generative_AItools_Course.pdf",
    "prompt": "Prompt_Engineering_Course.pdf"
}

@app.route("/send-pdf", methods=["POST"])
def send_pdf():
    try:
        data = request.get_json()
        email = data.get("email")
        payment_id = data.get("payment_id")
        course_ids = data.get("courses", [])

        if not email or not course_ids:
            return {"success": False, "error": "Missing email or courses"}, 400

        msg = EmailMessage()
        msg["Subject"] = "Your GB Academy Course PDFs"
        msg["From"] = os.environ.get("EMAIL")
        msg["To"] = email
        msg.set_content("Thank you for your payment! Attached are your course materials.")

        for cid in course_ids:
            filename = COURSE_MAP.get(cid)
            if not filename:
                continue
            if not os.path.exists(filename):
                print(f"Missing PDF: {filename}")
                continue
            with open(filename, "rb") as f:
                msg.add_attachment(
                    f.read(),
                    maintype="application",
                    subtype="pdf",
                    filename=filename
                )

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(os.environ["EMAIL"], os.environ["EMAIL_PASS"])
            smtp.send_message(msg)

        return {"success": True}
    except Exception as e:
        print("ERROR:", e)
        return {"success": False, "error": str(e)}, 500

@app.route("/", methods=["GET"])
def home():
    return "Server is running."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
