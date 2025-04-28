from flask import Flask, request, jsonify

app = Flask(__name__)
print_jobs = {}

@app.route("/orders", methods=["POST"])
def handle_post():
    content = request.get_json(force=True, silent=True)
    print("📨 Incoming POST:", content)
    
    # Handle printer heartbeat/status
    if content and 'status' in content:
        printer_mac = content.get('printerMAC')
        job_ready = printer_mac in print_jobs
        return jsonify({"jobReady": job_ready}), 200
    
    # Handle new print job coming from your system (curl/postman/etc.)
    printer_mac = content.get("printerMAC")
    job_data = content.get("data")
    if printer_mac and job_data:
        print_jobs[printer_mac] = {
            "jobToken": printer_mac + "_token",
            "mediaTypes": ["application/vnd.star.starprnt"],
            "data": job_data
        }
        print(f"🖨️ New job added for {printer_mac}")
        return jsonify({"message": "Job added!"}), 200
    
    return jsonify({"error": "Bad request"}), 400

@app.route("/orders", methods=["GET"])
def get_order():
    printer_mac = request.args.get("mac")
    if printer_mac in print_jobs:
        job_data = print_jobs.pop(printer_mac)
        response = {
            "jobToken": f"{printer_mac}_token",
            "mediaTypes": ["application/vnd.star.starprnt"],
            "data": job_data
        }
        print(f"📤 Sending job to {printer_mac}: {response}")
        return jsonify(response), 200
    else:
        print(f"❌ No job found for {printer_mac}")
        return jsonify({"jobReady": False}), 204



@app.route("/orders", methods=["DELETE"])
def delete_order():
    printer_mac = request.args.get("mac")
    if printer_mac and printer_mac in print_jobs:
        del print_jobs[printer_mac]
        print(f"🗑️ Deleted job for {printer_mac}")
        return "", 204
    return "", 404

@app.route("/")
def home():
    return "🖨️ CloudPRNT Server is Running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

