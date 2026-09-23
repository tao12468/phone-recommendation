const recommendList = document.querySelector("#recommend-list");
const phoneList = document.querySelector("#phone-list");
const healthBox = document.querySelector("#health");

function phoneCard(phone, extra = "") {
  return `
    <article class="phone-card">
      <div class="phone-name">${phone.name}</div>
      <div class="phone-meta">${phone.brand} · ${phone.position} · ¥${phone.price}</div>
      <ul>
        <li>屏幕：${phone.screen_size} 英寸</li>
        <li>电池：${phone.battery} mAh</li>
        <li>处理器：${phone.processor}</li>
        <li>场景：${phone.scenes.join("、")}</li>
      </ul>
      ${extra ? `<div class="extra">${extra}</div>` : ""}
    </article>
  `;
}

function renderRecommendations(items) {
  if (!items.length) {
    recommendList.innerHTML = '<p class="empty">暂无推荐结果</p>';
    return;
  }

  recommendList.innerHTML = items
    .map((item) =>
      phoneCard(
        item.phone,
        `推荐分：${item.score} · ${item.reason}`
      )
    )
    .join("");
}

function renderPhones(items) {
  if (!items.length) {
    phoneList.innerHTML = '<p class="empty">暂无手机数据</p>';
    return;
  }

  phoneList.innerHTML = items
    .map((phone) => phoneCard(phone))
    .join("");
}

async function loadHealth() {
  try {
    const response = await fetch("/api/health");
    const data = await response.json();
    healthBox.textContent = data.status === "ok" ? "服务正常" : "服务异常";
    healthBox.className = data.status === "ok" ? "health ok" : "health error";
  } catch (error) {
    healthBox.textContent = "无法连接服务";
    healthBox.className = "health error";
  }
}

async function loadPhones() {
  try {
    const response = await fetch("/api/phones");
    const data = await response.json();
    renderPhones(data.items);
  } catch (error) {
    phoneList.innerHTML = '<p class="empty">手机列表加载失败</p>';
  }
}

async function loadRecommendations() {
  const budget = document.querySelector("#budget").value;
  const brand = document.querySelector("#brand").value;
  const scene = document.querySelector("#scene").value;

  const params = new URLSearchParams();
  if (budget) params.set("budget", budget);
  if (brand) params.set("brand", brand);
  if (scene) params.set("scene", scene);

  try {
    const response = await fetch(`/api/recommendations?${params.toString()}`);
    const data = await response.json();
    renderRecommendations(data.items);
  } catch (error) {
    recommendList.innerHTML = '<p class="empty">推荐结果加载失败</p>';
  }
}

document.querySelector("#recommend-btn").addEventListener("click", loadRecommendations);
document.querySelector("#refresh-btn").addEventListener("click", loadPhones);

loadHealth();
loadPhones();
loadRecommendations();
