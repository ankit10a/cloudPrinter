from flask import Flask, request, Response

app = Flask(__name__)
print_jobs = {}

# StarPRNT Paper Cut Command
CUT_PAPER = b'\x1b\x64\x02'

@app.route("/orders", methods=["POST"])
def handle_post():
    content = request.get_json(force=True, silent=True)
    print(f"📨 Incoming POST: {content}")

    # Printer heartbeat check
    if content and 'status' in content:
        printer_mac = content.get('printerMAC')
        ready = printer_mac in print_jobs
        print(f"🔄 Heartbeat from {printer_mac}, jobReady={ready}")
        return {"jobReady": ready, "mediaTypes": ["application/vnd.star.starprnt"]}, 200

    # Receiving new print job from AI/curl
    printer_mac = content.get("printerMAC")
    job_text = content.get("data")

    if printer_mac and job_text:
        # Prepare formatted print job
        formatted_job = (job_text.strip() + "\n\n\n\n").encode('utf-8') + CUT_PAPER
        print_jobs[printer_mac] = formatted_job
        print(f"🖨️ Stored new job for printer {printer_mac}")
        return {"message": "Job stored and formatted!"}, 200

    print("⚠️ Bad POST received (missing printerMAC or data)")
    return {"error": "Bad request"}, 400

@app.route("/orders", methods=["GET"])
def get_order():
    printer_mac = request.args.get("mac")
    if printer_mac in print_jobs:
        job_data = print_jobs.pop(printer_mac)
        print(f"📤 Sending print job to printer {printer_mac}")
        return Response(
            job_data,
            status=200,
            content_type="application/vnd.star.starprnt"
        )
    print(f"❌ No job found for printer {printer_mac}")
    return Response(status=404)

@app.route("/orders", methods=["DELETE"])
def delete_order():
    printer_mac = request.args.get("mac")
    if printer_mac:
        print(f"🗑️ Printer {printer_mac} confirmed job deleted (printed successfully)")
    else:
        print("🗑️ Printer confirmed job deleted (no MAC found)")
    return "", 204

@app.route("/")
def home():
    return "🖨️ CloudPRNT Server Running!"

if __name__ == "__main__":
    print("🚀 Starting CloudPRNT server on port 5000...")
    app.run(host="0.0.0.0", port=5000)
