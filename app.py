from flask import Flask, request, Response

app = Flask(__name__)
print_jobs = {}

@app.route("/orders", methods=["POST"])
def handle_post():
    content = request.get_json(force=True, silent=True)
    
    if content and 'status' in content:
        printer_mac = content.get('printerMAC')
        return {"jobReady": printer_mac in print_jobs,
                "mediaTypes": ["application/vnd.star.starprnt"]}, 200
    
    printer_mac = content.get("printerMAC")
    job_data = content.get("data")
    if printer_mac and job_data:
        print_jobs[printer_mac] = job_data.encode("utf-8")  # store as bytes!
        return {"message": "Job stored!"}, 200
    
    return {"error": "Bad request"}, 400

@app.route("/orders", methods=["GET"])
def get_order():
    printer_mac = request.args.get("mac")
    if printer_mac in print_jobs:
        job_data = print_jobs.pop(printer_mac)
        return Response(
            job_data,
            status=200,
            content_type="application/vnd.star.starprnt"
        )
    return Response(status=404)

@app.route("/orders", methods=["DELETE"])
def delete_order():
    return "", 204

@app.route("/")
def home():
    return "CloudPRNT Server Running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
