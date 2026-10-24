/* CampusBuddy shared menu: a floating Menu button.
   To add a new page to the app, add one line to LINKS below. */
(function () {
  if (document.getElementById("cb-menu")) return;
  var LINKS = [
    ["Home", "/"],
    ["STUDENT MODE"],
    ["Events", "/static/register.html"],
    ["Find a place", "/static/student.html"],
    ["Report a problem", "/static/report.html"],
    ["ADMIN MODE"],
    ["Dashboard", "/static/index.html"],
    ["Greenest Block", "/static/leaderboard.html"],
    ["AI copilot", "/static/copilot.html"],
    ["Inbox", "/static/inbox.html"]
  ];

  var btn = document.createElement("button");
  btn.id = "cb-menu";
  btn.textContent = "Menu";
  btn.style.cssText = "position:fixed;top:12px;right:12px;z-index:100000;padding:9px 18px;border:0;" +
    "border-radius:20px;background:#E07B39;color:#fff;font:bold 14px Calibri,Segoe UI,sans-serif;" +
    "cursor:pointer;box-shadow:0 2px 8px rgba(0,0,0,.35)";

  var panel = document.createElement("div");
  panel.style.cssText = "position:fixed;top:54px;right:12px;z-index:100000;background:#fff;border-radius:14px;" +
    "padding:8px 0;min-width:200px;box-shadow:0 4px 16px rgba(0,0,0,.35);display:none;" +
    "font:15px Calibri,Segoe UI,sans-serif";
  panel.style.display = "none";

  var here = location.pathname;
  LINKS.forEach(function (item) {
    if (!item[1]) {
      var h = document.createElement("div");
      h.textContent = item[0];
      h.style.cssText = "padding:9px 18px 3px;font-size:11px;font-weight:bold;color:#8A7B6E;letter-spacing:1px";
      panel.appendChild(h);
      return;
    }
    var a = document.createElement("a");
    a.textContent = item[0];
    a.href = item[1];
    var current = here === item[1];
    a.style.cssText = "display:block;padding:8px 18px;text-decoration:none;color:#2F2A26;" +
      (current ? "background:#FBE3CF;font-weight:bold;" : "");
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
