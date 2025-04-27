from flask import Flask, request, jsonify

app = Flask(__name__)
print_jobs = {}

@app.route("/orders", methods=["POST"])
def handle_post():
    content = request.get_json(force=True, silent=True)
    
    # Handle printer heartbeat
    if content and 'status' in content:
        printer_mac = content.get('printerMAC')
        return jsonify({"jobReady": printer_mac in print_jobs}), 200
    
    # Handle job submission
    printer_mac = content.get("printerMAC")
    job_data = content.get("data")
    if printer_mac and job_data:
        print_jobs[printer_mac] = job_data
        return jsonify({"message": "Job added!"}), 200
    
    return jsonify({"error": "Bad request"}), 400

@app.route("/orders", methods=["GET"])
def get_order():
    printer_mac = request.args.get("mac")
    if printer_mac in print_jobs:
        job_data = print_jobs.pop(printer_mac)
        return job_data, 200, {"Content-Type": "application/vnd.star.starprnt"}
    return "", 204

@app.route("/orders", methods=["DELETE"])
def delete_order():
    return "", 200

 
# Health check
@app.route("/")
def home():
    return "CloudPRNT Server Running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
