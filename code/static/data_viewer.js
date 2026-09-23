const brandFilter = document.querySelector("#brand-filter");
const keywordInput = document.querySelector("#keyword");
const searchBtn = document.querySelector("#search-btn");
const prevBtn = document.querySelector("#prev-btn");
const nextBtn = document.querySelector("#next-btn");
const summaryBox = document.querySelector("#summary");
const tableBody = document.querySelector("#phone-table tbody");

let currentPage = 1;

async function loadBrands() {
  const response = await fetch("/api/db/brands");
  const data = await response.json();
  brandFilter.innerHTML = '<option value="">全部</option>' +
    data.items.map((brand) => `<option value="${brand}">${brand}</option>`).join("");
}

async function loadPhones() {
  const params = new URLSearchParams();
  params.set("page", currentPage);
  params.set("page_size", 20);
  if (brandFilter.value) params.set("brand", brandFilter.value);
  if (keywordInput.value) params.set("keyword", keywordInput.value);

  const response = await fetch(`/api/db/phones?${params.toString()}`);
  const data = await response.json();
  summaryBox.textContent = `共 ${data.total} 条`;
  summaryBox.className = "health ok";

  tableBody.innerHTML = data.items.map((phone) => `
    <tr>
      <td>${phone.source_id}</td>
      <td title="${phone.name || ""}">${phone.name || ""}</td>
      <td>${phone.brand || ""}</td>
      <td>${phone.price ?? ""}</td>
      <td>${phone.screen_size ?? ""}</td>
      <td>${phone.battery ?? ""}</td>
      <td>${phone.cpu || ""}</td>
      <td>${phone.ram ?? ""} / ${phone.rom ?? ""}</td>
      <td>${phone.os || ""}</td>
    </tr>
  `).join("");
}

searchBtn.addEventListener("click", () => {
  currentPage = 1;
  loadPhones();
});

prevBtn.addEventListener("click", () => {
  if (currentPage > 1) {
    currentPage -= 1;
    loadPhones();
  }
});

nextBtn.addEventListener("click", () => {
  currentPage += 1;
  loadPhones();
});

loadBrands();
loadPhones();
