var ROBOT = "\u{1F916}";
var D = { reports: [], events: [] };
var S = null;
var selected = "copilot";
var query = "";
var msgs = [];
var seen = {};
var lastSig = "";

function $(id) { return document.getElementById(id); }
function esc(s) {
  return String(s).replace(/[&<>"']/g, function (c) {
    return {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c];
  });
}
function nowText() { return new Date().toLocaleTimeString([], { hour:"numeric", minute:"2-digit" }); }

function post(url, body) {
  return fetch(url, { method:"POST", headers:{ "Content-Type":"application/json" }, body:JSON.stringify(body || {}) })
    .then(function (r) {
      return r.json().catch(function () { return {}; }).then(function (d) {
        if (!r.ok) throw new Error(d.detail || "Something went wrong");
        return d;
      });
    });
}

/* ---------- message list ---------- */
function evKey(e, i) { return "e" + (e.id !== undefined ? e.id : i); }

function items() {
  var list = [];
  var open = D.reports.filter(function (r) { return r.status === "open"; }).length;
  list.push({ key:"copilot", ico:ROBOT, bg:"#FBE3CF", title:"Copilot Assistant", isNew:true,
              prev: open + " open reports, " + D.events.length + " events", time:nowText(), unread:false });
  list.push({ key:"new", ico:"\u2795", bg:"#E3F1E8", title:"Create an event", prev:"Add a new campus event", time:"", unread:false });

  D.reports.slice().sort(function (a, b) { return b.ts - a.ts; }).forEach(function (r) {
    var isOpen = r.status === "open";
    list.push({ key:"r" + r.id, ico: isOpen ? "\u26A0\uFE0F" : "\u2705", bg: isOpen ? "#FFE3C8" : "#E3F1E8",
                title: r.kind + " at " + r.place, prev: r.note || "No note",
                time: new Date(r.ts * 1000).toLocaleDateString([], { day:"numeric", month:"short" }),
                unread: isOpen && !seen["r" + r.id] });
  });
  D.events.forEach(function (e, i) {
    var k = evKey(e, i);
    list.push({ key:k, ico:"\u{1F4E3}", bg:"#F9D9C8", title:e.title,
                prev: String(e.status).toUpperCase() + " | " + e.registered + " registered" + (e.feedback_count ? " | " + e.avg_rating + "/5" : ""),
                time:e.start_text, unread: !seen[k] });
  });
  return list;
}

function renderList() {
  var q = query.toLowerCase();
  var all = items();
  var shown = all.filter(function (i) { return !q || (i.title + " " + i.prev).toLowerCase().indexOf(q) >= 0; });
  $("items").innerHTML = shown.map(function (i) {
    return '<div class="it ' + (i.key === selected ? "sel" : "") + '" data-key="' + esc(i.key) + '">' +
      '<div class="ico" style="background:' + i.bg + '">' + i.ico + '</div>' +
      '<div class="tx"><b>' + esc(i.title) + (i.isNew ? '<span class="new">New</span>' : '') + '</b><span>' + esc(i.prev) + '</span></div>' +
      '<div class="mt">' + esc(i.time) + '<br>' + (i.unread ? '<span class="ud"></span>' : '') + '</div></div>';
  }).join("") || '<div class="it"><div class="tx"><span>No messages match.</span></div></div>';
  var n = all.filter(function (i) { return i.unread; }).length;
  $("count").textContent = n;
  $("navbadge").textContent = n;
  $("navbadge").style.display = n ? "" : "none";
}

/* ---------- copilot chat ---------- */
function appendBubble(m) {
  var box = $("msgs");
  if (!box) return;
  var row = document.createElement("div");
  row.className = "row" + (m.me ? " me" : "");
  row.innerHTML = (m.me ? "" : '<div class="av">' + ROBOT + '</div>') +
    '<div class="bub">' + esc(m.text).replace(/\n/g, "<br>") + '<small>' + esc(m.time) + '</small></div>';
  box.appendChild(row);
  box.scrollTop = box.scrollHeight;
}
function addMsg(text, me) {
  var m = { text:text, me:me, time:nowText() };
  msgs.push(m);
  if (selected === "copilot") appendBubble(m);
}

function answer(q) {
  q = q.toLowerCase();
  var open = D.reports.filter(function (r) { return r.status === "open"; });
  if (/report|problem|issue|complain/.test(q)) {
    return open.length
      ? open.length + " open report(s):\n" + open.map(function (r) { return "- " + r.kind + " at " + r.place + (r.note ? ": " + r.note : ""); }).join("\n")
      : "No open reports. Everything is resolved.";
  }
  if (/feedback|rating|comment|review/.test(q)) {
    var rated = D.events.filter(function (e) { return e.feedback_count; });
    return rated.length
      ? rated.map(function (e) { return e.title + ": " + e.avg_rating + "/5 from " + e.feedback_count + " response(s)"; }).join("\n")
      : "No event feedback yet.";
  }
  if (/event|register|student|hackathon/.test(q)) {
    return D.events.length
      ? D.events.map(function (e) { return e.title + " (" + String(e.status).toUpperCase() + "): " + e.registered + " registered at " + e.place; }).join("\n")
      : "No events yet. Click Create an event in the list.";
  }
  if (/energy|kwh|saved|rupee|saving|money/.test(q)) {
    return S ? S.saved_kwh.toFixed(1) + " kWh saved so far, about Rs " + Math.round(S.saved_rupees) + " (estimated)."
             : "I can't reach the live energy data right now.";
  }
  if (/people|crowd|occupied/.test(q)) {
    return S ? S.rooms.map(function (r) { return r.name + ": " + r.persons; }).join("\n") : "I can't reach the live data right now.";
  }
  return "I can tell you about open reports, event feedback, registrations, energy saved, or people per block. Try a button below.";
}
function send(text) {
  text = (text || "").trim();
  if (!text) return;
  addMsg(text, true);
  setTimeout(function () { addMsg(answer(text), false); }, 350);
}

/* ---------- right panel views ---------- */
function head(ico, title, sub) {
  return '<div class="ch"><div class="av">' + ico + '</div><div><b>' + esc(title) + '</b><span>' + sub + '</span></div></div>';
}

function showCopilot() {
  $("view").innerHTML =
    head(ROBOT, "Copilot Assistant", "Your AI guide at SJCIT \u2728") +
    '<div class="msgs" id="msgs"></div>' +
    '<div class="chips">' +
      '<button data-q="open reports">\u26A0\uFE0F Open reports</button>' +
      '<button data-q="event feedback">\u2B50 Event feedback</button>' +
      '<button data-q="registrations">\u{1F4C5} Registrations</button>' +
      '<button data-q="energy saved">\u{1F33F} Energy saved</button></div>' +
    '<div class="send"><input id="msg" type="text" placeholder="Type a message..."><button id="go">\u27A4</button></div>';
  msgs.forEach(appendBubble);
}

function showForm() {
  $("view").innerHTML = head("\u2795", "Create an event", "It appears on the Events page for students") +
    '<div class="detail form">' +
    '<label>Title</label><input id="t" placeholder="e.g. Tech talk">' +
    '<label>Place</label><input id="p" placeholder="e.g. Library">' +
    '<div class="two"><div><label>Starts in (minutes)</label><input id="s" type="number" value="5" min="0"></div>' +
    '<div><label>Duration (minutes)</label><input id="d" type="number" value="30" min="1"></div></div>' +
    '<label>Description</label><input id="desc" placeholder="What is it about?">' +
    '<button class="btn" onclick="createEvent()">Create event</button><span class="ok" id="cmsg"></span></div>';
}

function createEvent() {
  var out = $("cmsg");
  post("/api/events", {
    title: $("t").value,
    place: $("p").value,
    start_in_min: parseFloat($("s").value) || 0,
    duration_min: parseInt($("d").value) || 30,
    description: $("desc").value
  }).then(function () {
    out.style.color = ""; out.textContent = "Event created.";
    load();
  }).catch(function (e) { out.style.color = "#C0584A"; out.textContent = e.message; });
}

function resolveReport(id) {
  post("/api/reports/" + id + "/resolve").then(load).catch(function (e) { alert(e.message); });
}

function reportDetail(r) {
  var isOpen = r.status === "open";
  var when = new Date(r.ts * 1000).toLocaleString();
  $("view").innerHTML = head(isOpen ? "\u26A0\uFE0F" : "\u2705", r.kind + " at " + r.place,
      esc(when) + '<span class="tag ' + (isOpen ? "open" : "ended") + '">' + r.status.toUpperCase() + '</span>') +
    '<div class="detail"><h3>Note from the student</h3><div class="box">' + esc(r.note || "No note") + '</div>' +
    (isOpen ? '<button class="btn" onclick="resolveReport(' + Number(r.id) + ')">Mark resolved</button>'
            : '<div class="meta">This report is resolved.</div>') + '</div>';
}

function eventDetail(e) {
  var rating = (e.avg_rating !== null && e.avg_rating !== undefined)
    ? "Average rating " + e.avg_rating + "/5 from " + e.feedback_count : "No feedback yet";
  var comments = (e.comments || []).map(function (c) {
    return '<div class="box">' + esc(c.rating) + '/5 ' + esc(c.comment) + '</div>';
  }).join("") || '<div class="meta">No comments.</div>';
  var people = (e.people || []).map(function (p) {
    return '<div class="box">' + esc(p.name) + ' (' + esc(p.usn) + ')</div>';
  }).join("") || '<div class="meta">Nobody yet.</div>';
  var cls = e.status === "ended" ? "ended" : (e.status === "live" ? "live" : "");
  $("view").innerHTML = head("\u{1F4E3}", e.title,
      esc(e.place) + '<span class="tag ' + cls + '">' + String(e.status).toUpperCase() + '</span>') +
    '<div class="detail"><div class="meta">' + esc(e.start_text) + ' | ' + esc(e.duration_min) + ' min | ' +
    esc(e.registered) + ' registered | ' + esc(rating) + '</div>' +
    '<h3>Feedback comments</h3>' + comments +
    '<h3>Registered students</h3>' + people + '</div>';
}

function currentItem() {
  if (selected.charAt(0) === "r" && selected !== "copilot") {
    return D.reports.filter(function (r) { return "r" + r.id === selected; })[0] || null;
  }
  if (selected.charAt(0) === "e") {
    var found = null;
    D.events.forEach(function (e, i) { if (evKey(e, i) === selected) found = e; });
    return found;
  }
  return null;
}

function showView() {
  if (selected === "copilot") return showCopilot();
  if (selected === "new") return showForm();
  var it = currentItem();
  if (!it) { selected = "copilot"; return showCopilot(); }
  if (selected.charAt(0) === "r") reportDetail(it); else eventDetail(it);
}

function choose(key) {
  selected = key;
  seen[key] = true;
  showView();
  var it = currentItem();
  lastSig = it ? JSON.stringify(it) : "";
  renderList();
}

/* ---------- live data ---------- */
function load() {
  fetch("/api/admin/inbox", { cache:"no-store" })
    .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
    .then(function (d) {
      D = { reports: d.reports || [], events: d.events || [] };
      renderList();
      if (selected !== "copilot" && selected !== "new") {
        var it = currentItem();
        var sig = it ? JSON.stringify(it) : "";
        if (sig !== lastSig) { lastSig = sig; showView(); }
      }
    })
    .catch(function (e) { console.log(e); });
  fetch("/api/state", { cache:"no-store" })
    .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
    .then(function (s) {
      S = s;
      $("kwhpill").textContent = "\u{1F33F} " + s.saved_kwh.toFixed(1) + " kWh saved";
    })
    .catch(function (e) { console.log(e); });
}

/* ---------- events ---------- */
$("items").addEventListener("click", function (e) {
  var el = e.target.closest(".it");
  if (el && el.dataset.key) choose(el.dataset.key);
});
$("view").addEventListener("click", function (e) {
  if (e.target.dataset && e.target.dataset.q) send(e.target.dataset.q);
  if (e.target.id === "go") { send($("msg").value); $("msg").value = ""; }
});
$("view").addEventListener("keydown", function (e) {
  if (e.key === "Enter" && e.target.id === "msg") { send(e.target.value); e.target.value = ""; }
});
$("search").addEventListener("input", function (e) { query = e.target.value; renderList(); });

addMsg("Hi! Here is what I can help with:\n\u26A0\uFE0F Problem reports from students\n\u2B50 Event feedback and ratings\n\u{1F4C5} Registrations\n\u{1F33F} Energy saved\nAsk me anything or tap a button below.", false);
showCopilot();
renderList();
load();
setInterval(load, 5000);