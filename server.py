from flask import Flask, request
import smtplib
from email.message import EmailMessage
import os

app = Flask(__name__)

COURSE_MAP = {
    "powerbi": "Power_BI_Course.pdf",
    "genai": "Generative_AItools_Course.pdf",
    "prompt": "Prompt_Engineering_Course.pdf"
}

@app.route("/send-pdf", methods=["POST"])
def send_pdf():
    data = request.get_json()
    email = data.get("email")
    payment_id = data.get("payment_id")
    course_ids = data.get("courses", [])

    msg = EmailMessage()
    msg["Subject"] = "Your Course Materials - GB Academy"
    msg["From"] = os.environ["EMAIL"]
    msg["To"] = email
    msg.set_content("Thank you for your purchase. Find attached your course PDFs.")

    for cid in course_ids:
        path = COURSE_MAP.get(cid)
        if path and os.path.exists(path):
            with open(path, "rb") as f:
                msg.add_attachment(f.read(), maintype="application", subtype="pdf", filename=path)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(os.environ["EMAIL"], os.environ["EMAIL_PASS"])
        smtp.send_message(msg)

    return "PDFs sent", 200

if __name__ == '__main__':
     import os
port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port)

