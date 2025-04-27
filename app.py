from flask import Flask, request, make_response

app = Flask(__name__)

# In-memory print queue (key: printer MAC, value: job data)
print_jobs = {}

# CloudPRNT polling endpoint (GET)
@app.route("/orders", methods=["GET"])
def get_order():
    printer_mac = request.args.get("mac")
    print(f"📥 Printer {printer_mac} requested job!")

    if not printer_mac or printer_mac not in print_jobs:
        # No job → return 204 No Content
        return "", 204

    # Get job data and send as plain text
    job_data = print_jobs[printer_mac]
    response = make_response(job_data)
    response.headers["Content-Type"] = "text/plain"  # Required for printer
    del print_jobs[printer_mac]  # Remove job after retrieval
    return response

# Job completion endpoint (DELETE)
@app.route("/orders", methods=["DELETE"])
def delete_order():
    printer_mac = request.args.get("mac")
    print(f"🗑️ Printer {printer_mac} deleted job.")
    return "", 200

# Add a print job (called by your ordering system)
@app.route("/orders", methods=["POST"])
def add_order():
    content = request.json
    printer_mac = content.get("printerMAC")
    job_data = content.get("data")

    if printer_mac and job_data:
        # Escape StarPRNT commands if needed (e.g., \x1b for ESC)
        print_jobs[printer_mac] = job_data
        print(f"🖨️ Added job for printer {printer_mac}: {job_data}")
        return "", 200
    else:
        return "Invalid request", 400

# Health check
@app.route("/")
def home():
    return "CloudPRNT Server Running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
