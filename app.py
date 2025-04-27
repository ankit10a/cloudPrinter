from flask import Flask, request, make_response, jsonify  # ✅ Added jsonify

app = Flask(__name__)

# In-memory print queue (key: printer MAC, value: job data)
print_jobs = {}

# CloudPRNT polling endpoint (GET)
@app.route("/orders", methods=["POST"])
def handle_post():
    content = request.get_json(force=True, silent=True)
    print("📨 Incoming POST:", content)

    # Case 1: Printer is sending a heartbeat/status update
 if content and 'status' in content:
        printer_mac = content.get('printerMAC')
        return jsonify({"jobReady": printer_mac in print_jobs}), 200
            print("🖨️ Job ready for printer", printer_mac)

    # Case 2: Your ordering system is adding a job
    printer_mac = content.get("printerMAC")
    job_data = content.get("data")
    if printer_mac and job_data:
        print_jobs[printer_mac] = job_data
        print(f"✅ Added job for {printer_mac}: {job_data}")
        return jsonify({"message": "Job added!"}), 200

    # Invalid request
    print("❌ Invalid POST request")
    return jsonify({"error": "Bad request"}), 400

# Printer GETs the job (plain text)
@app.route("/orders", methods=["GET"])
def get_order():
    printer_mac = request.args.get("mac")
    print(f"📥 Printer {printer_mac} requested job")
    
    if printer_mac in print_jobs:
        job_data = print_jobs.pop(printer_mac)
         return job_data, 200, {"Content-Type": "application/vnd.star.starprnt"}
    return "", 204  

# Printer confirms job completion
@app.route("/orders", methods=["DELETE"])
def delete_order():
   
    return "", 200

# Health check
@app.route("/")
def home():
    return "CloudPRNT Server Running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
