var LABEL = { occupied:"Occupied", empty_lights_on:"Empty, lights on", warning:"Warning", switched_off:"Switched off" };

function esc(s) {
  return String(s).replace(/[&<>"']/g, function (c) {
    return {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c];
  });
}
function setText(id, v) { var el = document.getElementById(id); if (el) el.textContent = v; }

function loadState() {
  return fetch("/api/state", { cache: "no-store" })
    .then(function (r) {
      if (!r.ok) throw new Error("/api/state returned " + r.status);
      return r.json();
    })
    .then(function (s) {
      var rooms = s.rooms || [];
      var people = 0;
      rooms.forEach(function (r) { people += (r.persons || 0); });
      setText("people", people);
      setText("kwh", Number(s.saved_kwh || 0).toFixed(1));
      setText("rs", Math.round(Number(s.saved_rupees || 0)));
      document.getElementById("blocks").innerHTML = rooms.map(function (r) {
        return '<div class="blk ' + esc(r.status) + '"><b>' + esc(r.name) + '</b><span>' +
               esc(LABEL[r.status] || r.status) + '<br>' + (r.persons || 0) + ' people</span></div>';
      }).join("");
      setText("status", "Live data connected. Updated " + new Date().toLocaleTimeString());
    })
    .catch(function (e) {
      setText("status", "Could not load live data: " + e.message);
      console.log(e);
    });
}

/* The one event today: Hackathon demo, 9:00 AM to 4:00 PM */
function updateEvent() {
  var now = new Date();
  var mins = now.getHours() * 60 + now.getMinutes();
  var tag = document.getElementById("evtag");
  if (mins < 9 * 60) {
    tag.textContent = "UPCOMING"; tag.className = "tag"; setText("evs", 1);
  } else if (mins < 16 * 60) {
    tag.textContent = "LIVE"; tag.className = "tag live"; setText("evs", 1);
  } else {
    tag.textContent = "ENDED"; tag.className = "tag ended"; setText("evs", 0);
  }
}

function refresh() { loadState(); updateEvent(); }
refresh();
setInterval(refresh, 3000);