const authPanel = document.querySelector("#auth-panel");
const mainPanel = document.querySelector("#main-panel");
const authMessage = document.querySelector("#auth-message");
const loginUser = document.querySelector("#login-user");
const logoutBtn = document.querySelector("#logout-btn");
const navHome = document.querySelector("#nav-home");
const navFavorites = document.querySelector("#nav-favorites");
const navCompare = document.querySelector("#nav-compare");
const resultList = document.querySelector("#result-list");
const favoritesView = document.querySelector("#favorites-view");
const favoritesContent = document.querySelector("#favorites-content");
const compareView = document.querySelector("#compare-view");
const compareContent = document.querySelector("#compare-content");
const detailModal = document.querySelector("#detail-modal");
const detailContent = document.querySelector("#detail-content");
const closeDetail = document.querySelector("#close-detail");
const compareBar = document.querySelector("#compare-bar");
const compareInfo = document.querySelector("#compare-info");
const compareClear = document.querySelector("#compare-clear");
const compareGo = document.querySelector("#compare-go");

let imageMap = {};
let compareIds = [];

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
  navFavorites.classList.remove("hidden");
  navCompare.classList.remove("hidden");
  showHomeView();
  loginUser.textContent = user.username;
  loginUser.className = "health ok";
}

function showLoggedOut() {
  authPanel.classList.remove("hidden");
  mainPanel.classList.add("hidden");
  favoritesView.classList.add("hidden");
  compareView.classList.add("hidden");
  logoutBtn.classList.add("hidden");
  navFavorites.classList.add("hidden");
  navCompare.classList.add("hidden");
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
  const chip = (value, label) =>
    value !== null && value !== undefined && value !== ""
      ? `<span class="chip">${label}${value}</span>`
      : "";
  return `
    <article class="phone-card" data-source="${item.source_id}">
      ${imageBlock}
      <div class="phone-name">${item.name}</div>
      <div class="phone-meta">${item.brand}</div>
      <div class="phone-price">¥${item.price}</div>
      <div class="chip-row">
        ${chip(item.screen_size ? item.screen_size + "英寸" : "", "屏幕")}
        ${chip(item.battery ? item.battery + "mAh" : "", "电池")}
        ${chip(item.ram ? item.ram + "GB" : "", "内存")}
        ${chip(item.rom ? item.rom + "GB" : "", "存储")}
        ${chip(item.position, "定位")}
      </div>
      <div class="card-foot">
        <span class="score">推荐分 ${item.score}</span>
        <div class="card-actions">
          <button class="fav-btn" data-source="${item.source_id}">收藏</button>
          <button class="compare-btn" data-source="${item.source_id}">对比</button>
        </div>
      </div>
    </article>
  `;
}

function detailRow(label, value) {
  if (!value && value !== 0) return "";
  return `<div class="detail-row"><span>${label}</span><span>${value}</span></div>`;
}

async function openDetail(sourceId, fallbackItem) {
  detailContent.innerHTML = '<p class="empty">加载中...</p>';
  detailModal.classList.remove("hidden");
  try {
    const response = await fetch(`/api/phones/detail/${sourceId}`);
    const phone = await response.json();
    const imageUrl = phone.image_url || imageMap[String(sourceId)] || "";
    const imageBlock = imageUrl
      ? `<img class="detail-img" src="${imageUrl}" alt="${phone.name}" />`
      : "";
    detailContent.innerHTML = `
      ${imageBlock}
      <h2>${phone.name || fallbackItem.name}</h2>
      <div class="phone-meta">${phone.brand || fallbackItem.brand}</div>
      <div class="phone-price">¥${phone.price}</div>
      <div class="detail-grid">
        ${detailRow("屏幕尺寸", phone.screen_size ? phone.screen_size + " 英寸" : "")}
        ${detailRow("分辨率", phone.resolution)}
        ${detailRow("电池容量", phone.battery ? phone.battery + " mAh" : "")}
        ${detailRow("核心数", phone.core_count)}
        ${detailRow("摄像头", phone.camera)}
        ${detailRow("CPU", phone.cpu)}
        ${detailRow("内存", phone.ram ? phone.ram + " GB" : "")}
        ${detailRow("存储", phone.rom ? phone.rom + " GB" : "")}
        ${detailRow("系统", phone.os)}
        ${detailRow("使用场景", phone.usage_scenes)}
        ${detailRow("发布时间", phone.release_date)}
      </div>
    `;
  } catch (error) {
    detailContent.innerHTML = '<p class="empty">详情加载失败</p>';
  }
}

function closeDetailModal() {
  detailModal.classList.add("hidden");
}

function collectChecked(selector) {
  return Array.from(document.querySelectorAll(`${selector} input:checked`)).map(
    (input) => input.value
  );
}

function setActiveNav(activeButton) {
  [navHome, navFavorites, navCompare].forEach((button) => {
    button.classList.toggle("active", button === activeButton);
  });
}

function showHomeView() {
  mainPanel.classList.remove("hidden");
  favoritesView.classList.add("hidden");
  compareView.classList.add("hidden");
  setActiveNav(navHome);
}

function showFavoritesView() {
  mainPanel.classList.add("hidden");
  favoritesView.classList.remove("hidden");
  compareView.classList.add("hidden");
  setActiveNav(navFavorites);
  loadFavorites();
}

function showCompareView() {
  mainPanel.classList.add("hidden");
  favoritesView.classList.add("hidden");
  compareView.classList.remove("hidden");
  setActiveNav(navCompare);
}

async function loadRecommendations() {
  const budget = document.querySelector("#budget").value;
  const brand = collectChecked("#brand-options");
  const scene = collectChecked("#scene-options");
  const os = document.querySelector("#os").value;

  const params = new URLSearchParams();
  if (budget) params.set("budget", budget);
  if (brand.length) params.set("brand", brand.join(","));
  if (scene.length) params.set("scene", scene.join(","));
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

function toggleCompare(sourceId) {
  const stringId = String(sourceId);
  const index = compareIds.indexOf(stringId);
  if (index >= 0) {
    compareIds.splice(index, 1);
  } else if (compareIds.length >= 3) {
    alert("最多同时对比 3 款手机");
    return;
  } else {
    compareIds.push(stringId);
  }
  updateCompareBar();
}

function updateCompareBar() {
  compareInfo.textContent = `已选 ${compareIds.length} 款`;
  compareBar.classList.toggle("hidden", compareIds.length === 0);
}

function compareRow(label, values) {
  return `
    <tr>
      <th>${label}</th>
      ${values.map((value) => `<td>${value || "-"}</td>`).join("")}
    </tr>
  `;
}

async function openCompare() {
  if (compareIds.length < 2) {
    alert("请至少选择 2 款手机进行对比");
    return;
  }
  const response = await fetch(`/api/phones/compare?ids=${compareIds.join(",")}`);
  const data = await response.json();
  const phones = data.items;
  const rows = [
    ["图片", phones.map((phone) => phone.image_url ? `<img class="compare-img" src="${phone.image_url}" alt="" />` : "-")],
    ["名称", phones.map((phone) => phone.name)],
    ["品牌", phones.map((phone) => phone.brand)],
    ["价格", phones.map((phone) => "¥" + phone.price)],
    ["屏幕尺寸", phones.map((phone) => phone.screen_size ? phone.screen_size + " 英寸" : "-")],
    ["分辨率", phones.map((phone) => phone.resolution)],
    ["电池容量", phones.map((phone) => phone.battery ? phone.battery + " mAh" : "-")],
    ["核心数", phones.map((phone) => phone.core_count)],
    ["摄像头", phones.map((phone) => phone.camera)],
    ["CPU", phones.map((phone) => phone.cpu)],
    ["内存", phones.map((phone) => phone.ram ? phone.ram + " GB" : "-")],
    ["存储", phones.map((phone) => phone.rom ? phone.rom + " GB" : "-")],
    ["系统", phones.map((phone) => phone.os)],
    ["使用场景", phones.map((phone) => phone.usage_scenes)],
    ["发布时间", phones.map((phone) => phone.release_date)],
  ];
  compareContent.innerHTML = `
    <h2>机型对比</h2>
    <div class="table-wrap">
      <table>
        <tbody>
          ${rows.map((row) => compareRow(row[0], row[1])).join("")}
        </tbody>
      </table>
    </div>
  `;
  showCompareView();
}

compareClear.addEventListener("click", () => {
  compareIds = [];
  updateCompareBar();
});
compareGo.addEventListener("click", openCompare);

async function loadFavorites() {
  favoritesContent.innerHTML = '<p class="empty">加载中...</p>';
  const response = await fetch("/api/me/favorites", {
    headers: { Authorization: `Bearer ${token()}` },
  });
  const data = await response.json();
  if (!data.items.length) {
    favoritesContent.innerHTML = '<p class="empty">你还没有收藏手机</p>';
    return;
  }
  favoritesContent.innerHTML = data.items
    .map((phone) => {
      const imageUrl = phone.image_url || imageMap[String(phone.source_id)] || "";
      const imageBlock = imageUrl
        ? `<img class="phone-img" src="${imageUrl}" alt="${phone.name}" />`
        : `<div class="phone-img placeholder">${(phone.brand || "手").slice(0, 1)}</div>`;
      const chip = (value, label) =>
        value !== null && value !== undefined && value !== ""
          ? `<span class="chip">${label}${value}</span>`
          : "";
      return `
        <article class="phone-card" data-source="${phone.source_id}">
          ${imageBlock}
          <div class="phone-name">${phone.name}</div>
          <div class="phone-meta">${phone.brand}</div>
          <div class="phone-price">¥${phone.price}</div>
          <div class="chip-row">
            ${chip(phone.screen_size ? phone.screen_size + "英寸" : "", "屏幕")}
            ${chip(phone.battery ? phone.battery + "mAh" : "", "电池")}
            ${chip(phone.ram ? phone.ram + "GB" : "", "内存")}
            ${chip(phone.rom ? phone.rom + "GB" : "", "存储")}
          </div>
          <div class="card-foot">
            <span class="score">已收藏</span>
            <div class="card-actions">
              <button class="unfav-btn" data-source="${phone.source_id}">取消收藏</button>
              <button class="compare-btn" data-source="${phone.source_id}">对比</button>
            </div>
          </div>
        </article>
      `;
    })
    .join("");
}

navHome.addEventListener("click", showHomeView);
navFavorites.addEventListener("click", showFavoritesView);
navCompare.addEventListener("click", () => {
  if (compareIds.length < 2) {
    showCompareView();
    compareContent.innerHTML = '<p class="empty">请先在卡片上选择 2 款手机，再点击“开始对比”。</p>';
    return;
  }
  openCompare();
});

document.addEventListener("click", async (event) => {
  const unfavButton = event.target.closest(".unfav-btn");
  if (unfavButton) {
    const sourceId = unfavButton.getAttribute("data-source");
    await fetch(`/api/me/favorites/${sourceId}`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${token()}` },
    });
    loadFavorites();
    return;
  }

  const compareButton = event.target.closest(".compare-btn");
  if (compareButton) {
    toggleCompare(compareButton.getAttribute("data-source"));
    return;
  }

  const button = event.target.closest(".fav-btn");
  if (button) {
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
    return;
  }

  const card = event.target.closest(".phone-card");
  if (card) {
    openDetail(card.getAttribute("data-source"), { name: card.querySelector(".phone-name")?.textContent });
  }
});

closeDetail.addEventListener("click", closeDetailModal);
detailModal.addEventListener("click", (event) => {
  if (event.target === detailModal) closeDetailModal();
});

checkLogin();
loadImages();
