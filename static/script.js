document.addEventListener("DOMContentLoaded", function () {
    fetchReconciliationReport();
});

function uploadFiles() {
    let bankFile = document.getElementById("bankFile").files[0];
    let ledgerFile = document.getElementById("ledgerFile").files[0];

    if (!bankFile || !ledgerFile) {
        alert("Please upload both bank and ledger files.");
        return;
    }

    let formData = new FormData();
    formData.append("bankFile", bankFile);
    formData.append("ledgerFile", ledgerFile);

    fetch("http://127.0.0.1:5000/upload", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert("Upload failed: " + data.error);
        } else {
            alert(data.message);
            fetchReconciliationReport();
        }
    })
    .catch(error => {
        console.error("Error uploading files:", error);
        alert("Error uploading files. Check the console for details.");
    });
}

function fetchReconciliationReport() {
    fetch("http://127.0.0.1:5000/report")
        .then(response => {
            if (!response.ok) {
                throw new Error("Failed to fetch report. Server returned: " + response.status);
            }
            return response.json();
        })
        .then(data => {
            populateReportTable(data);
        })
        .catch(error => console.error("Error fetching report:", error));
}

function populateReportTable(reportData) {
    let tbody = document.querySelector("#reportTable tbody");
    tbody.innerHTML = "";

    reportData.forEach(row => {
        let tr = document.createElement("tr");
        tr.innerHTML = `
            <td>${row.date || "N/A"}</td>
            <td>${row.description || "N/A"}</td>
            <td>${row.debit !== undefined ? row.debit : "-"}</td>
            <td>${row.credit !== undefined ? row.credit : "-"}</td>
            <td>${row.balance !== undefined ? row.balance : "-"}</td>
            <td>${row.status || "Pending"}</td>
        `;
        tbody.appendChild(tr);
    });
}

function downloadReport() {
    window.location.href = "http://127.0.0.1:5000/download-report";
}
