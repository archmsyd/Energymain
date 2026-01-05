const statusText = document.getElementById("statusText");
const createJobButton = document.getElementById("createJob");

createJobButton.addEventListener("click", () => {
  const fileInput = document.getElementById("pdfInput");
  const track = document.getElementById("trackSelect").value;
  const scale = document.getElementById("scaleInput").value;

  if (!fileInput.files.length) {
    statusText.textContent = "Please select a PDF first.";
    return;
  }

  statusText.textContent = `Job created locally · Track ${track.toUpperCase()} · Scale ${scale}`;
});
