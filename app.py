from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import pandas as pd
from reconciliation_logic import reconcile_transactions

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

UPLOAD_FOLDER = "uploads"
REPORT_FOLDER = "reports"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(REPORT_FOLDER, exist_ok=True)

@app.route("/upload", methods=["POST"])
def upload_files():
    try:
        if "bankFile" not in request.files or "ledgerFile" not in request.files:
            return jsonify({"error": "Both files are required"}), 400

        bank_file = request.files["bankFile"]
        ledger_file = request.files["ledgerFile"]

        if not bank_file.filename.endswith(".csv") or not ledger_file.filename.endswith(".csv"):
            return jsonify({"error": "Only CSV files are allowed"}), 400

        bank_path = os.path.join(UPLOAD_FOLDER, "bank.csv")
        ledger_path = os.path.join(UPLOAD_FOLDER, "ledger.csv")
        bank_file.save(bank_path)
        ledger_file.save(ledger_path)

        # Perform reconciliation
        report_path = os.path.join(REPORT_FOLDER, "reconciliation_report.csv")
        reconciled, unreconciled_bank, unreconciled_ledger = reconcile_transactions(bank_path, ledger_path, report_path)

        return jsonify({
            "message": "Reconciliation completed!",
            "reconciled_count": len(reconciled),
            "unreconciled_bank_count": len(unreconciled_bank),
            "unreconciled_ledger_count": len(unreconciled_ledger)
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/report", methods=["GET"])
def get_report():
    try:
        report_path = os.path.join(REPORT_FOLDER, "reconciliation_report.csv")
        if not os.path.exists(report_path):
            return jsonify({"error": "No reconciliation report available"}), 404

        df = pd.read_csv(report_path)
        return jsonify(df.to_dict(orient="records"))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/download-report", methods=["GET"])
def download_report():
    report_path = os.path.join(REPORT_FOLDER, "reconciliation_report.csv")
    if os.path.exists(report_path):
        return send_file(report_path, as_attachment=True, download_name="reconciliation_report.csv")
    return jsonify({"error": "No report available"}), 404

if __name__ == "__main__":
    app.run(debug=True)
