from flask import Flask, request, jsonify

app = Flask(__name__)

# In-memory print queue
print_jobs = {
    "order_101": {
        "jobReady": True,
        "mediaTypes": ["text"],
        "jobToken": "order_101",
        "data": "Order #101\n1x Paneer Roll ₹80\n1x Limca ₹40\nTotal: ₹120\n\nThank you!"
    }
}

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

# Optional: just to check server is live
@app.route("/", methods=["GET"])
def home():
    return "🖨️ CloudPRNT Server is Running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
