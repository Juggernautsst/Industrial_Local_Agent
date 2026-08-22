"use strict";

const state = {
  token: "",
  subjectId: "user-alice",
  busy: false,
};

const elements = {
  accessError: document.getElementById("access-error"),
  auditCount: document.getElementById("audit-count"),
  auditEmpty: document.getElementById("audit-empty"),
  auditTableBody: document.getElementById("audit-table-body"),
  emptyResult: document.getElementById("empty-result"),
  identitySelector: document.getElementById("identity-selector"),
  policyVersion: document.getElementById("policy-version"),
  queryPreset: document.getElementById("query-preset"),
  resetButton: document.getElementById("reset-button"),
  resultStream: document.getElementById("result-stream"),
  retrieveButton: document.getElementById("retrieve-button"),
  shareState: document.getElementById("share-state"),
  tenantMap: document.getElementById("tenant-map"),
};

function extractToken() {
  const fragment = new URLSearchParams(window.location.hash.slice(1));
  const token = fragment.get("token") || window.sessionStorage.getItem("e2-demo-token") || "";
  if (token) {
    window.sessionStorage.setItem("e2-demo-token", token);
  }
  window.history.replaceState(null, "", window.location.pathname);
  return token;
}

function makeElement(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function setError(message) {
  elements.accessError.hidden = !message;
  elements.accessError.textContent = message || "";
}

function setBusy(value) {
  state.busy = value;
  document.querySelectorAll("button, select").forEach((control) => {
    control.disabled = value || !state.token;
  });
}

async function request(path, options = {}) {
  const headers = new Headers(options.headers || {});
  headers.set("X-E2-Demo-Token", state.token);
  const response = await fetch(path, { ...options, headers });
  const payload = await response.json();
  if (!response.ok) {
    throw new Error(payload.error || `Request failed (${response.status})`);
  }
  return payload;
}

function renderIdentities(users) {
  elements.identitySelector.replaceChildren();
  users.forEach((user) => {
    const button = makeElement("button", "identity-button");
    button.type = "button";
    button.dataset.subjectId = user.subject_id;
    if (user.subject_id === state.subjectId) button.classList.add("active");
    const displayName = user.subject_id.replace("user-", "");
    button.append(
      makeElement("strong", "", displayName.charAt(0).toUpperCase() + displayName.slice(1)),
      makeElement("small", "", `${user.tenant_id} / ${user.role}`),
    );
    button.addEventListener("click", () => {
      state.subjectId = user.subject_id;
      renderIdentities(users);
    });
    elements.identitySelector.append(button);
  });
}

function renderTenantMap(sources, isShared) {
  elements.tenantMap.replaceChildren();
  const grouped = new Map();
  sources.forEach((source) => {
    if (!grouped.has(source.tenant_id)) grouped.set(source.tenant_id, []);
    grouped.get(source.tenant_id).push(source);
  });
  grouped.forEach((tenantSources, tenantId) => {
    const row = makeElement("div", "tenant-row");
    row.append(makeElement("span", "tenant-id", tenantId));
    const list = makeElement("div", "source-list");
    tenantSources.forEach((source) => {
      const chip = makeElement("span", "source-chip", `${source.source_id} / ${source.owner_id}`);
      if (source.source_id === "source-a2" && isShared) chip.classList.add("shared");
      list.append(chip);
    });
    row.append(list);
    elements.tenantMap.append(row);
  });
}

function renderAudit(events) {
  elements.auditTableBody.replaceChildren();
  elements.auditEmpty.hidden = events.length > 0;
  events.slice().reverse().forEach((event) => {
    const row = document.createElement("tr");
    const values = [
      event.sequence,
      event.subject_id || "-",
      event.tenant_id,
      event.source_ids.length ? event.source_ids.join(", ") : "none",
      `${event.event_hash.slice(0, 10)}...`,
    ];
    values.forEach((value) => row.append(makeElement("td", "", String(value))));
    elements.auditTableBody.append(row);
  });
}

function renderState(snapshot) {
  elements.policyVersion.textContent = String(snapshot.policy_version);
  elements.auditCount.textContent = String(snapshot.audit_event_count);
  elements.shareState.textContent = snapshot.source_a2_shared_with_alice
    ? "source-a2: shared with Alice"
    : "source-a2: private";
  elements.shareState.classList.toggle("shared", snapshot.source_a2_shared_with_alice);
  renderIdentities(snapshot.users);
  renderTenantMap(snapshot.sources, snapshot.source_a2_shared_with_alice);
  renderAudit(snapshot.audit_events);
}

function resultDetails(result) {
  const details = [];
  const fields = [
    ["subject", result.subject_id],
    ["tenant", result.tenant_id],
    ["policy", result.policy_version],
    ["sources", Array.isArray(result.source_ids) ? result.source_ids.join(", ") || "none" : undefined],
    ["bundle", result.bundle_id ? `${result.bundle_id.slice(0, 12)}...` : undefined],
    ["events", result.event_count],
    ["reason", result.reason],
  ];
  fields.forEach(([label, value]) => {
    if (value !== undefined && value !== null) details.push(`${label}=${value}`);
  });
  return details;
}

function addResult(result) {
  elements.emptyResult.hidden = true;
  const item = makeElement("article", `result-item ${result.kind}`);
  const labels = {
    allow: "ALLOW",
    deny: "DENY",
    error: "ERROR",
    no_evidence: "NO EVIDENCE",
    pass: "PASS",
  };
  item.append(makeElement("span", "result-status", labels[result.kind] || "RESULT"));
  const content = makeElement("div", "result-content");
  content.append(makeElement("h3", "", result.title));
  const details = makeElement("div", "result-details");
  resultDetails(result).forEach((detail) => details.append(makeElement("span", "detail-chip", detail)));
  content.append(details);
  item.append(content);
  elements.resultStream.prepend(item);
}

async function execute(action, extra = {}) {
  if (state.busy) return;
  setBusy(true);
  setError("");
  try {
    const payload = await request("/api/action", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action, ...extra }),
    });
    addResult(payload.result);
    renderState(payload.state);
  } catch (error) {
    setError(error.message);
  } finally {
    setBusy(false);
  }
}

function bindActions() {
  elements.retrieveButton.addEventListener("click", () => {
    execute("retrieve", {
      subject_id: state.subjectId,
      query: elements.queryPreset.value,
    });
  });
  document.querySelectorAll("[data-action]").forEach((button) => {
    button.addEventListener("click", () => execute(button.dataset.action));
  });
  elements.resetButton.addEventListener("click", async () => {
    elements.resultStream.replaceChildren();
    elements.emptyResult.hidden = true;
    await execute("reset");
  });
}

async function start() {
  state.token = extractToken();
  bindActions();
  if (!state.token) {
    setError("Missing startup token / 缺少启动令牌。请使用服务器输出的完整 URL。");
    setBusy(false);
    return;
  }
  setBusy(true);
  try {
    const snapshot = await request("/api/state");
    renderState(snapshot);
    setError("");
  } catch (error) {
    setError(error.message);
  } finally {
    setBusy(false);
  }
}

start();
