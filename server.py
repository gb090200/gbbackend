
from flask import Flask, request
import smtplib
from email.message import EmailMessage
import os
import json

app = Flask(__name__)

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

        # Check that variables exist
        print("EMAIL:", email)
        print("COURSES:", course_ids)

        msg = EmailMessage()
        msg["Subject"] = "Your Course Materials - GB Academy"
        msg["From"] = os.environ.get("EMAIL")
        msg["To"] = email
        msg.set_content("Thank you for your payment. Attached are your courses.")

        for cid in course_ids:
            filename = COURSE_MAP.get(cid)
            if not filename:
                print(f"Course ID not found in map: {cid}")
                continue
            if not os.path.exists(filename):
                print(f"Missing PDF file: {filename}")
                continue
            with open(filename, "rb") as f:
                msg.add_attachment(
                    f.read(), maintype="application", subtype="pdf", filename=filename
                )

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(os.environ["EMAIL"], os.environ["EMAIL_PASS"])
            smtp.send_message(msg)

        return {"success": True}
    except Exception as e:
        print("ERROR:", str(e))
        return {"success": False, "error": str(e)}, 500


@app.route("/log-txn", methods=["POST"])
def log_txn():
    data = request.get_json()
    email = data.get("email")
    txn = data.get("txn")

    if not email or not txn:
        return {"success": False, "error": "Missing fields"}, 400

    try:
        if os.path.exists("transactions.json"):
            with open("transactions.json", "r") as f:
                records = json.load(f)
        else:
            records = []

        records.append({"email": email, "txn": txn})
        with open("transactions.json", "w") as f:
            json.dump(records, f, indent=2)

        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}, 500

@app.route("/upi-webhook", methods=["POST"])
def upi_webhook():
    sms = request.json.get("message", "")
    if not sms:
        return {"success": False, "error": "Missing message"}, 400

    if not os.path.exists("transactions.json"):
        return {"success": False, "error": "No transactions logged"}, 404

    with open("transactions.json", "r") as f:
        records = json.load(f)

    for record in records:
        if record["txn"] in sms:
            try:
                email = record["email"]
                course_ids = ["powerbi", "genai", "prompt"]  # Update if needed
                data = {
                    "email": email,
                    "payment_id": "upi_sms_auto",
                    "courses": course_ids
                }
                with app.test_request_context(json=data):
                    send_pdf()
                return {"success": True, "matched_email": email}
            except Exception as e:
                return {"success": False, "error": str(e)}, 500

    return {"success": False, "error": "No matching txn"}, 404

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

