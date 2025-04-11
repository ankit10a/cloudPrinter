from flask import Flask, request, jsonify

app = Flask(__name__)

# In-memory print queue
print_jobs = {}

# Add a new print job
@app.route("/orders", methods=["POST"])
def add_order():
    content = request.json
    job_token = content.get("jobToken")
    job_data = content.get("data")

    if not job_token or not job_data:
        return jsonify({"error": "Missing jobToken or data"}), 400

    print_jobs[job_token] = {
        "jobReady": True,
        "mediaTypes": ["text"],
        "jobToken": job_token,
        "data": job_data
    }

    return jsonify({"message": f"Job {job_token} added successfully"})

# Printer polls this to fetch next print job
@app.route("/orders", methods=["GET"])
def get_order():
    print("📥 Printer requested job!")  # Logging for debug
    if not print_jobs:
        return jsonify({"jobReady": False})

    job_token, job_data = next(iter(print_jobs.items()))
    return jsonify(job_data)

# Printer confirms print job done → delete it
@app.route("/orders/<job_token>", methods=["DELETE"])
def delete_order(job_token):
    if job_token in print_jobs:
        del print_jobs[job_token]
        return "", 204
    return "Job not found", 404

# Server health check
@app.route("/", methods=["GET"])
def home():
    return "🖨️ CloudPRNT Server is Running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
