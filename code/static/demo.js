const statusBox = document.querySelector("#status");
const resultList = document.querySelector("#result-list");
const recommendBtn = document.querySelector("#recommend-btn");
const prefBtn = document.querySelector("#pref-btn");

function card(item) {
  return `
    <article class="phone-card">
      <div class="phone-name">${item.name}</div>
      <div class="phone-meta">${item.brand} · ¥${item.price}</div>
      <ul>
        <li>推荐分：${item.score}</li>
        <li>来源：${item.reason}</li>
        ${item.position ? `<li>定位：${item.position}</li>` : ""}
      </ul>
      <button class="fav-btn" data-source="${item.source_id}">收藏这款</button>
    </article>
  `;
}

function renderItems(items) {
  if (!items.length) {
    resultList.innerHTML = '<p class="empty">暂无推荐结果</p>';
    return;
  }
  resultList.innerHTML = items.map(card).join("");
}

async function loadRecommendations() {
  const userId = document.querySelector("#user-id").value || 1;
  const budget = document.querySelector("#budget").value;
  const brand = document.querySelector("#brand").value;
  const scene = document.querySelector("#scene").value;
  const os = document.querySelector("#os").value;

  const params = new URLSearchParams();
  params.set("user_id", userId);
  if (budget) params.set("budget", budget);
  if (brand) params.set("brand", brand);
  if (scene) params.set("scene", scene);
  if (os) params.set("os", os);

  statusBox.textContent = "加载中...";
  try {
    const response = await fetch(`/api/recommendations/hybrid?${params.toString()}`);
    const data = await response.json();
    renderItems(data.items);
    statusBox.textContent = "已更新";
    statusBox.className = "health ok";
  } catch (error) {
    statusBox.textContent = "加载失败";
    statusBox.className = "health error";
  }
}

async function loadPreferences() {
  const userId = document.querySelector("#user-id").value || 1;
  try {
    const response = await fetch(`/api/preferences/${userId}`);
    const data = await response.json();
    alert(
      "预算：" + (data.budget ? Math.round(data.budget) : "暂无") +
      "\n品牌偏好：" + JSON.stringify(data.brand_counts) +
      "\n场景偏好：" + JSON.stringify(data.scene_counts)
    );
  } catch (error) {
    alert("暂无偏好数据");
  }
}

document.addEventListener("click", async (event) => {
  const button = event.target.closest(".fav-btn");
  if (!button) return;
  const sourceId = button.getAttribute("data-source");
  const userId = document.querySelector("#user-id").value || 1;
  await fetch("/api/behavior", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      user_id: Number(userId),
      phone_source_id: Number(sourceId),
      event_type: "favorite",
    }),
  });
  button.textContent = "已收藏";
});

recommendBtn.addEventListener("click", loadRecommendations);
prefBtn.addEventListener("click", loadPreferences);

loadRecommendations();
