const authPanel = document.querySelector("#auth-panel");
const mainPanel = document.querySelector("#main-panel");
const authMessage = document.querySelector("#auth-message");
const loginUser = document.querySelector("#login-user");
const logoutBtn = document.querySelector("#logout-btn");
const resultList = document.querySelector("#result-list");

let imageMap = {};

async function loadImages() {
  try {
    const response = await fetch("/api/phone-images");
    imageMap = await response.json();
  } catch (error) {
    imageMap = {};
  }
}

function token() {
  return localStorage.getItem("token") || "";
}

function showLoggedIn(user) {
  authPanel.classList.add("hidden");
  mainPanel.classList.remove("hidden");
  logoutBtn.classList.remove("hidden");
  loginUser.textContent = user.username;
  loginUser.className = "health ok";
}

function showLoggedOut() {
  authPanel.classList.remove("hidden");
  mainPanel.classList.add("hidden");
  logoutBtn.classList.add("hidden");
  loginUser.textContent = "";
}

async function checkLogin() {
  if (!token()) {
    showLoggedOut();
    return;
  }
  const response = await fetch("/api/auth/me", {
    headers: { Authorization: `Bearer ${token()}` },
  });
  if (response.ok) {
    showLoggedIn(await response.json());
    loadRecommendations();
  } else {
    localStorage.removeItem("token");
    showLoggedOut();
  }
}

async function loginOrRegister(mode) {
  const username = document.querySelector("#username").value;
  const password = document.querySelector("#password").value;
  authMessage.textContent = "";
  const response = await fetch(`/api/auth/${mode}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
  const data = await response.json();
  if (!response.ok) {
    authMessage.textContent = data.error || "操作失败";
    return;
  }
  localStorage.setItem("token", data.token);
  showLoggedIn(data.user);
  loadRecommendations();
}

function card(item) {
  const imageUrl = imageMap[String(item.source_id)] || "";
  const imageBlock = imageUrl
    ? `<img class="phone-img" src="${imageUrl}" alt="${item.name}" onerror="this.style.display='none'" />`
    : `<div class="phone-img placeholder">${(item.brand || "手").slice(0, 1)}</div>`;
  return `
    <article class="phone-card">
      ${imageBlock}
      <div class="phone-name">${item.name}</div>
      <div class="phone-meta">${item.brand} · ¥${item.price}</div>
      <ul>
        <li>推荐分：${item.score}</li>
        ${item.position ? `<li>定位：${item.position}</li>` : ""}
      </ul>
      <button class="fav-btn" data-source="${item.source_id}">收藏这款</button>
    </article>
  `;
}

async function loadRecommendations() {
  const budget = document.querySelector("#budget").value;
  const brand = document.querySelector("#brand").value;
  const scene = document.querySelector("#scene").value;
  const os = document.querySelector("#os").value;

  const params = new URLSearchParams();
  if (budget) params.set("budget", budget);
  if (brand) params.set("brand", brand);
  if (scene) params.set("scene", scene);
  if (os) params.set("os", os);

  const response = await fetch(`/api/recommendations/hybrid?${params.toString()}`, {
    headers: { Authorization: `Bearer ${token()}` },
  });
  const data = await response.json();
  resultList.innerHTML = data.items.length
    ? data.items.map(card).join("")
    : '<p class="empty">暂无推荐结果</p>';
}

async function loadPreferences() {
  const response = await fetch("/api/me/preferences", {
    headers: { Authorization: `Bearer ${token()}` },
  });
  const data = await response.json();
  alert(
    "预算：" + (data.budget ? Math.round(data.budget) : "暂无") +
    "\n品牌偏好：" + JSON.stringify(data.brand_counts) +
    "\n场景偏好：" + JSON.stringify(data.scene_counts)
  );
}

document.querySelector("#login-btn").addEventListener("click", () => loginOrRegister("login"));
document.querySelector("#register-btn").addEventListener("click", () => loginOrRegister("register"));
document.querySelector("#recommend-btn").addEventListener("click", loadRecommendations);
document.querySelector("#pref-btn").addEventListener("click", loadPreferences);
logoutBtn.addEventListener("click", () => {
  localStorage.removeItem("token");
  showLoggedOut();
});

document.addEventListener("click", async (event) => {
  const button = event.target.closest(".fav-btn");
  if (!button) return;
  const sourceId = button.getAttribute("data-source");
  await fetch("/api/behavior", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token()}`,
    },
    body: JSON.stringify({
      phone_source_id: Number(sourceId),
      event_type: "favorite",
    }),
  });
  button.textContent = "已收藏";
});

checkLogin();
loadImages();
