// static/js/teams.js
console.log("⚙️ teams.js loaded");

// After the DOM loads, wire up all “⇄” buttons:
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".swap-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      const li = btn.closest("li");
      const source = li.parentElement;
      const target = source.id === "team-a"
        ? document.getElementById("team-b")
        : document.getElementById("team-a");
      target.appendChild(li);
      syncHiddenInputs();
    });
  });
  syncHiddenInputs();
});

function syncHiddenInputs() {
  const form = document.getElementById("confirm-form");
  // remove old hidden inputs
  form.querySelectorAll("input[name='team_a[]'], input[name='team_b[]']")
      .forEach(i => i.remove());

  // add for Team A
  document.querySelectorAll("#team-a li").forEach(li => {
    const id = li.dataset.playerId;
    const inp = document.createElement("input");
    inp.type = "hidden";
    inp.name = "team_a[]";
    inp.value = id;
    form.appendChild(inp);
  });

  // add for Team B
  document.querySelectorAll("#team-b li").forEach(li => {
    const id = li.dataset.playerId;
    const inp = document.createElement("input");
    inp.type = "hidden";
    inp.name = "team_b[]";
    inp.value = id;
    form.appendChild(inp);
  });
}
