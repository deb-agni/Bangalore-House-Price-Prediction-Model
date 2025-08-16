async function loadLocations() {
  const res = await fetch("/get_location_names");
  const data = await res.json();
  const sel = document.getElementById("uiLocations");
  sel.innerHTML = "";
  (data.locations || []).forEach(loc => {
    const opt = document.createElement("option");
    opt.value = loc;
    opt.textContent = loc;
    sel.appendChild(opt);
  });
}

function populateNumbers(id, max) {
  const el = document.getElementById(id);
  for (let i = 1; i <= max; i++) {
    const opt = document.createElement("option");
    opt.value = i;
    opt.textContent = i;
    el.appendChild(opt);
  }
}

async function estimate() {
  const sqft = Number(document.getElementById("uiSqft").value);
  const bath = Number(document.getElementById("uiBathrooms").value);
  const bhk  = Number(document.getElementById("uiBHK").value);
  const loc  = document.getElementById("uiLocations").value;

  const res = await fetch("/predict_home_price", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ total_sqft: sqft, bath: bath, bhk: bhk, location: loc })
  });
  const data = await res.json();
  const out = document.getElementById("uiEstimatedPrice");
  if (data.estimated_price_lakh !== undefined) {
    out.textContent = `Estimated Price: ₹ ${data.estimated_price_lakh} lakh`;
  } else if (data.error) {
    out.textContent = "Error: " + data.error;
  } else {
    out.textContent = "Unexpected response";
  }
}

window.addEventListener("DOMContentLoaded", () => {
  populateNumbers("uiBathrooms", 5);
  populateNumbers("uiBHK", 5);
  loadLocations();
  document.getElementById("estimateBtn").addEventListener("click", estimate);
});
