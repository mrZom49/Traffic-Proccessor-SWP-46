const POLL_INTERVAL_MS = 1000;

const elements = {
  statusDiode: document.getElementById("status-diode"),
  primaryLabel: document.getElementById("primary-label"),
  primaryValue: document.getElementById("primary-value"),
  secondaryValue: document.getElementById("rate-value"),
  packetTypes: document.getElementById("packet-types"),
  modeButton: document.getElementById("mode-button"),
  packetCounts: {
    tcp_packets: document.getElementById("tcp-packets"),
    udp_packets: document.getElementById("udp-packets"),
    icmp_packets: document.getElementById("icmp-packets"),
    other_packets: document.getElementById("other-packets"),
  },
};

const emptyStats = {
  status: "offline",
  total_packets: 0,
  total_bytes: 0,
  packets_per_second: 0,
  bytes_per_second: 0,
  tcp_packets: 0,
  udp_packets: 0,
  icmp_packets: 0,
  other_packets: 0,
};

const state = {
  mode: "bytes",
  stats: { ...emptyStats },
};

function getStatsEndpoint() {
  const params = new URLSearchParams(window.location.search);
  const configuredEndpoint = params.get("api");

  if (configuredEndpoint) {
    return configuredEndpoint;
  }

  const runsOutsideBackend =
    window.location.protocol === "file:" ||
    (["localhost", "127.0.0.1"].includes(window.location.hostname) &&
      window.location.port !== "8080");

  return runsOutsideBackend
    ? "http://localhost:8080/packets"
    : `${window.location.origin}/packets`;
}

const statsEndpoint = getStatsEndpoint();

function formatNumber(value) {
  return Number(value || 0).toLocaleString();
}

function renderBytesMode(stats) {
  elements.primaryLabel.textContent = "Bytes per second";
  elements.primaryValue.textContent = `${formatNumber(stats.bytes_per_second)} B/s`;
  elements.secondaryValue.textContent = `${formatNumber(stats.total_bytes)} total bytes`;
  elements.packetTypes.hidden = true;
  elements.modeButton.textContent = "Show packets";
}

function renderPacketsMode(stats) {
  elements.primaryLabel.textContent = "Packets per second";
  elements.primaryValue.textContent = `${formatNumber(stats.packets_per_second)} packets/s`;
  elements.secondaryValue.textContent = `${formatNumber(stats.total_packets)} total packets`;
  elements.packetTypes.hidden = false;
  elements.modeButton.textContent = "Show bytes";

  Object.entries(elements.packetCounts).forEach(([key, node]) => {
    node.textContent = formatNumber(stats[key]);
  });
}

function render() {
  const isOnline = state.stats.status === "online";

  elements.statusDiode.classList.toggle("offline", !isOnline);

  if (state.mode === "packets") {
    renderPacketsMode(state.stats);
  } else {
    renderBytesMode(state.stats);
  }

  if (!isOnline) {
    elements.secondaryValue.textContent = "Waiting for backend data";
  }
}

async function loadStats() {
  try {
    const response = await fetch(statsEndpoint, { cache: "no-store" });
    if (!response.ok) {
      throw new Error(`Backend returned ${response.status}`);
    }

    state.stats = { ...emptyStats, ...(await response.json()) };
  } catch {
    state.stats = { ...state.stats, status: "offline" };
  }

  render();
}

elements.modeButton.addEventListener("click", () => {
  state.mode = state.mode === "bytes" ? "packets" : "bytes";
  render();
});

render();
loadStats();

const pollTimer = window.setInterval(loadStats, POLL_INTERVAL_MS);

window.addEventListener("beforeunload", () => {
  window.clearInterval(pollTimer);
});
