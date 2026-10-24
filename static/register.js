var EV = [];
var SU = [];

function esc(s) {
  return String(s).replace(/[&<>"']/g, function (c) {
    return {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c];
  });
}
function keyOf(e) { return String(e.id !== undefined ? e.id : e.title); }
function countOf(e) {
  var k = keyOf(e);
  return (e.registered || 0) + SU.filter(function (s) { return s.event === k; }).length;
}

/* Hide repeated events (same title and place), keep the first one */
function unique(list) {
  var seen = {};
  return list.filter(function (e) {
    var k = (String(e.title) + "|" + String(e.place)).toLowerCase();
    if (seen[k]) return false;
    seen[k] = true;
    return true;
  });
}

function render() {
  var box = document.getElementById("list");
  if (!EV.length) {
    box.innerHTML = '<div class="card empty">No events yet. An admin can create one in the Inbox.</div>';
    return;
  }
  box.innerHTML = EV.map(function (e, i) {
    var st = String(e.status || "").toLowerCase();
    var open = st !== "ended";
    var cls = st === "live" ? "live" : (st === "ended" ? "ended" : "");
    var win = open
      ? '<div class="window">Registration is open now and closes when the event ends</div>'
      : '<div class="window closed">Registration is closed. This event has ended.</div>';
    var form = open
      ? '<div class="reg">' +
          '<input id="nm' + i + '" type="text" placeholder="Your name">' +
          '<input id="em' + i + '" type="email" placeholder="Your email address">' +
          '<button class="btn" data-i="' + i + '">Register now</button>' +
          '<div class="msg" id="ms' + i + '"></div></div>'
      : "";
    return '<div class="card"><h2>' + esc(e.title) + '<span class="tag ' + cls + '">' + esc(st.toUpperCase()) + '</span></h2>' +
      '<div class="meta">' + esc(e.place) + ' | ' + esc(e.start_text) + ' | ' + esc(e.duration_min) + ' min</div>' +
      (e.description ? '<div class="desc">' + esc(e.description) + '</div>' : '') +
      win + '<div class="count">' + countOf(e) + ' registered</div>' + form + '</div>';
  }).join("");
}

function load() {
  var a = document.activeElement;
  if (a && a.tagName === "INPUT") return;
  Promise.all([
    fetch("/api/events", { cache:"no-store" }).then(function (r) { return r.json(); }),
    fetch("/api/signups", { cache:"no-store" }).then(function (r) { return r.ok ? r.json() : []; }).catch(function () { return []; })
  ]).then(function (res) {
    EV = unique(Array.isArray(res[0]) ? res[0] : []);
    SU = Array.isArray(res[1]) ? res[1] : [];
    render();
  }).catch(function (e) {
    document.getElementById("list").innerHTML = '<div class="card empty">Could not load events: ' + esc(e.message) + '</div>';
  });
}

document.getElementById("list").addEventListener("click", function (ev) {
  var i = ev.target.getAttribute("data-i");
  if (i === null) return;
  var e = EV[i];
  var out = document.getElementById("ms" + i);
  fetch("/api/signups", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      event: keyOf(e),
      name: document.getElementById("nm" + i).value,
      email: document.getElementById("em" + i).value
    })
  }).then(function (r) {
    return r.json().catch(function () { return {}; }).then(function (d) {
      if (!r.ok) throw new Error(d.detail || "Could not register");
      SU.push({ event: keyOf(e), email: "x" });
      out.className = "msg ok";
      out.textContent = "You are registered! " + countOf(e) + " people have registered so far.";
      document.getElementById("em" + i).value = "";
      document.getElementById("nm" + i).value = "";
    });
  }).catch(function (err) {
    out.className = "msg bad";
    out.textContent = err.message;
  });
});

load();
setInterval(load, 4000);