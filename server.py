from flask import Flask, request, jsonify
from job_tracker_gui import handle_external_submit  # 👈 Add this function to your existing code

app = Flask(__name__)

@app.route('/submit-job', methods=['POST'])
def submit_job():
    data = request.json
    url = data.get("url")
    if not url:
        return jsonify({"error": "Missing URL"}), 400

    try:
        handle_external_submit(url)
        return jsonify({"message": "Job submitted successfully."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=5000)
