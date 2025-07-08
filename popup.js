document.getElementById("export").addEventListener("click", () => {
  chrome.storage.local.get("leads", ({ leads }) => {
    let csv = "Company,Website\n";
    leads.forEach(l => {
      csv += `${l.company},${l.website}\n`;
    });
    const blob = new Blob([csv], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    chrome.downloads.download({ url, filename: "leads.csv" });
  });
});
