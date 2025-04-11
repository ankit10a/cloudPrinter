from flask import Flask, request, jsonify

app = Flask(__name__)

# In-memory print queue
print_jobs = {}

# Add print job (AI or client calls this)
@app.route("/orders", methods=["POST"])
def add_order():
    data = request.json
    if not data or "jobToken" not in data or "data" not in data:
        return jsonify({"error": "Invalid job format"}), 400
    
    job_token = data["jobToken"]
    print_jobs[job_token] = {
        "jobReady": True,
        "mediaTypes": ["text"],
        "jobToken": job_token,
        "data": data["data"]
    }
    return jsonify({"message": f"Job {job_token} added successfully"}), 200

# Printer calls this to get next job
@app.route("/orders", methods=["GET"])
def get_order():
    if not print_jobs:
        return jsonify({"jobReady": False})
    
    job_token, job_data = next(iter(print_jobs.items()))
    return jsonify(job_data)

# Printer calls this to delete printed job
@app.route("/orders/<job_token>", methods=["DELETE"])
def delete_order(job_token):
    if job_token in print_jobs:
        del print_jobs[job_token]
        return "", 204
    return "Job not found", 404

# Optional: Server live check
@app.route("/", methods=["GET"])
def home():
    return "🖨️ CloudPRNT Server is Running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
