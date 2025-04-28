from flask import Flask, request, jsonify

app = Flask(__name__)
print_jobs = {}

@app.route("/orders", methods=["POST"])
def handle_post():
    content = request.get_json(force=True, silent=True)
    print("📨 Incoming POST:", content)

    # — Printer heartbeat/status check —
    if content and 'status' in content:
        printer_mac = content.get('printerMAC')
        ready = printer_mac in print_jobs
        print(f"🖨️ Heartbeat from {printer_mac}, jobReady={ready}")
        return jsonify({"jobReady": ready}), 200

    # — New job submission (from curl/your AI) —
    printer_mac = content.get("printerMAC") if content else None
    job_data    = content.get("data")       if content else None

    if printer_mac and job_data:
        # Store the raw text (we’ll wrap it below)
        print_jobs[printer_mac] = job_data
        print(f"✅ New job stored for {printer_mac}")
        return jsonify({"message": "Job added!"}), 200

    # — Anything else —
    print("⚙️ Unknown POST, ignored")
    return jsonify({"status": "ignored"}), 200

@app.route("/orders", methods=["GET"])
def handle_get():
    printer_mac = request.args.get("mac")
    if printer_mac in print_jobs:
        job_data = print_jobs.pop(printer_mac)

        # Build the exact JSON the Star printer expects:
        response = {
            "jobReady": True,
            "jobToken": f"{printer_mac.replace(':','')}_token",
            "mediaTypes": ["application/vnd.star.starprnt"],
            "jobType": "raw",
            "printData": job_data
        }
        print(f"📤 Sending job to {printer_mac}: {response}")
        return jsonify(response), 200

    print(f"❌ No job for {printer_mac}")
    return jsonify({"jobReady": False}), 200

@app.route("/orders", methods=["DELETE"])
def handle_delete():
    # Printer confirms completion via DELETE?mac=...&code=...
    printer_mac = request.args.get("mac")
    if printer_mac in print_jobs:
        del print_jobs[printer_mac]
        print(f"🗑️ Deleted job for {printer_mac}")
        return "", 204
    return "", 404

@app.route("/")
def home():
    return "🖨️ CloudPRNT Server is Running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
