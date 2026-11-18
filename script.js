const DAYS = ["MON", "TUE", "WED", "THU", "FRI"];
const DAY_NAMES = { MON: "Monday", TUE: "Tuesday", WED: "Wednesday", THU: "Thursday", FRI: "Friday" };
let classData = {};

document.addEventListener("DOMContentLoaded", async () => {
  applySavedTheme();
  document.getElementById("themeToggle").addEventListener("click", toggleTheme);
  document.getElementById("lookupForm").addEventListener("submit", event => {
    event.preventDefault();
    lookupClass();
  });

  const savedRoll = localStorage.getItem("lastRoll") || "";
  const rollInput = document.getElementById("rollInput");
  if (savedRoll) rollInput.value = savedRoll;

  const today = new Date().getDay(); // Sunday = 0
  const dayIndex = today === 0 ? 0 : Math.min(today - 1, 4);
  document.getElementById("daySelect").value = DAYS[dayIndex];

  await loadClassData();
  if (savedRoll) lookupClass();
});

async function loadClassData() {
  const result = document.getElementById("result");
  try {
    const response = await fetch("./timetable.json", { cache: "no-store" });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    classData = await response.json();
    if (!classData || typeof classData !== "object" || Array.isArray(classData)) {
      throw new Error("The timetable JSON must be an object keyed by roll number.");
    }
  } catch (error) {
    console.error("Could not load timetable:", error);
    result.innerHTML = '<p class="error">Could not load timetable.json. Make sure the file exists and run the project using a local web server.</p>';
  }
}

function lookupClass() {
  const roll = document.getElementById("rollInput").value.trim().toUpperCase();
  const selectedDay = document.getElementById("daySelect").value;
  const result = document.getElementById("result");

  if (!roll) {
    result.innerHTML = '<p class="error">Please enter your roll number.</p>';
    return;
  }
  localStorage.setItem("lastRoll", roll);

  const schedule = classData[roll];
  if (!schedule) {
    result.innerHTML = '<p class="error">Roll number not found. Check the roll number and try again.</p>';
    return;
  }

  const next = getNextAvailableClass(schedule, DAYS.indexOf(selectedDay));
  if (!next) {
    result.innerHTML = '<p class="info">No classes are listed for this roll number this week.</p>';
    return;
  }

  document.getElementById("daySelect").value = next.day;
  let html = `
    <h2 class="result-heading">Schedule for <span class="roll">${escapeHTML(roll)}</span> on
    <span class="day">${DAY_NAMES[next.day]}</span></h2>
    ${renderDayTable(next.classes)}
    <details class="week-details">
      <summary>📅 View full week's schedule</summary>
      <div>`;

  DAYS.forEach(day => {
    const dayClasses = schedule[day];
    if (dayClasses && hasClasses(dayClasses)) {
      html += `<h3 class="week-day day">${DAY_NAMES[day]}</h3>${renderDayTable(dayClasses)}`;
    }
  });
  html += "</div></details>";
  result.innerHTML = html;
}

function getNextAvailableClass(schedule, startIndex) {
  for (let offset = 0; offset < DAYS.length; offset++) {
    const day = DAYS[(startIndex + offset) % DAYS.length];
    const classes = schedule[day];
    if (classes && hasClasses(classes)) return { day, classes };
  }
  return null;
}

function hasClasses(classes) {
  return Object.values(classes).some(subject => isRealClass(subject));
}

function isRealClass(subject) {
  if (subject === null || subject === undefined) return false;
  const value = String(subject).trim();
  return value !== "" && value.toUpperCase() !== "X" && value.toLowerCase() !== "no class";
}

function renderDayTable(classes) {
  const times = Object.keys(classes).sort((a, b) => timeToNumber(a) - timeToNumber(b));
  const rows = times
    .filter(time => isRealClass(classes[time]))
    .map(time => `<tr><td>${escapeHTML(time)}</td><td>${escapeHTML(String(classes[time]))}</td></tr>`)
    .join("");

  if (!rows) return '<p class="empty-state">No classes scheduled for this day.</p>';
  return `<div class="table-wrap"><table><thead><tr><th>Time</th><th>Subject</th></tr></thead><tbody>${rows}</tbody></table></div>`;
}

function timeToNumber(value) {
  const match = String(value).match(/(\d{1,2})(?::(\d{2}))?/);
  return match ? Number(match[1]) * 60 + Number(match[2] || 0) : Number.MAX_SAFE_INTEGER;
}

function escapeHTML(value) {
  return value.replace(/[&<>"']/g, char => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
  })[char]);
}

function toggleTheme() {
  const current = document.documentElement.dataset.theme || "light";
  const next = current === "dark" ? "light" : "dark";
  document.documentElement.dataset.theme = next;
  localStorage.setItem("theme", next);
  updateThemeButton(next);
}

function applySavedTheme() {
  const theme = localStorage.getItem("theme") || "light";
  document.documentElement.dataset.theme = theme;
  updateThemeButton(theme);
}

function updateThemeButton(theme) {
  const button = document.getElementById("themeToggle");
  if (button) button.textContent = theme === "dark" ? "☀️ Light Mode" : "🌙 Dark Mode";
}
