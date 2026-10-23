/* CampusBuddy shared menu: a floating Menu button on every page.
   To add a new page to the app, add one line to LINKS below. */
(function () {
  if (document.getElementById("cb-menu")) return;
  var LINKS = [
    ["Home", "/"],
    ["STUDENT MODE"],
    ["Events", "/static/events.html"],
    ["Find a place", "/static/student.html"],
    ["Report a problem", "/static/report.html"],
    ["Report a problem", "/static/report.html"],
    ["Campus map", "/static/map.html"],
    ["ADMIN MODE"],
    ["Dashboard", "/static/admin.html"],
    ["Greenest Block", "/static/leaderboard.html"],
    ["Floor view", "/static/index.html"],
    ["AI copilot", "/static/copilot.html"],
    ["Inbox", "/static/inbox.html"]
  ];

  var btn = document.createElement("button");
  btn.id = "cb-menu";
  btn.textContent = "Menu";
  btn.style.cssText = "position:fixed;top:10px;right:10px;z-index:100000;padding:8px 14px;border:0;" +
    "border-radius:20px;background:#0f3d2e;color:#fff;font:bold 14px Calibri,Segoe UI,sans-serif;" +
    "cursor:pointer;box-shadow:0 2px 8px rgba(0,0,0,.4)";

  var panel = document.createElement("div");
  panel.style.cssText = "position:fixed;top:50px;right:10px;z-index:100000;background:#fff;border-radius:12px;" +
    "padding:8px 0;min-width:190px;box-shadow:0 4px 14px rgba(0,0,0,.4);display:none;" +
    "font:14px Calibri,Segoe UI,sans-serif";
  panel.style.display = "none";

  var here = location.pathname;
  LINKS.forEach(function (item) {
    if (!item[1]) {
      var h = document.createElement("div");
      h.textContent = item[0];
      h.style.cssText = "padding:8px 16px 2px;font-size:11px;font-weight:bold;color:#5b6b63;letter-spacing:1px";
      panel.appendChild(h);
      return;
    }
    var a = document.createElement("a");
    a.textContent = item[0];
    a.href = item[1];
    var current = here === item[1];
    a.style.cssText = "display:block;padding:7px 16px;text-decoration:none;color:#1b2b24;" +
      (current ? "background:#eaf4ec;font-weight:bold;" : "");
    panel.appendChild(a);
  });

  btn.addEventListener("click", function (e) {
    e.stopPropagation();
    panel.style.display = panel.style.display === "none" ? "block" : "none";
  });
  document.addEventListener("click", function () { panel.style.display = "none"; });

  document.body.appendChild(btn);
  document.body.appendChild(panel);
})();