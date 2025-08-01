const chart_type_btn = document.getElementsByClassName('table-type-button')[0].getElementsByTagName('img')[0];
const periodElements = document.querySelectorAll('button.chart-button');
let periodButtons = []
for (var i = 0; i < periodElements.length; i++) {
  periodButtons.push(periodElements[i].id);
};

const choosePeriod = (event) => {
  periodButtons.forEach(id => {
    document.getElementById(id).classList.remove('active');
  });

  const clickedBtn = event.currentTarget;
  clickedBtn.classList.add('active');
  localStorage.setItem('selectedPeriod', clickedBtn.id);

  const selectedPeriod = clickedBtn.id.replace('_btn', '');
  if (selectedPeriod != 'custom') {
    const el = document.getElementsByClassName('hidden_custom')[0]
    let duration = 400;
    el.style.height = el.scrollHeight + 'px';
    el.style.overflow = 'hidden';
    el.offsetHeight;
    el.style.transition = `height ${duration}ms ease, opacity ${duration}ms ease`;
    el.style.height = '0';
    el.style.opacity = '0';
    setTimeout(() => {
      el.style.display = 'none';
      el.style.removeProperty('height');
      el.style.removeProperty('overflow');
      el.style.removeProperty('transition');
      el.style.removeProperty('opacity');
    }, duration);

    renderTotalLine(selectedPeriod);
    renderVisibleChart(selectedPeriod);
  } else {
    const el = document.getElementsByClassName('hidden_custom')[0]
    let duration = 400;
    el.style.removeProperty('display'); // прибираємо display:none
    let display = window.getComputedStyle(el).display;
    if (display === 'none') display = 'block';
    el.style.display = display;
    const height = el.scrollHeight + 'px';
    el.style.overflow = 'hidden';
    el.style.height = '0';
    el.style.opacity = '0';
    el.offsetHeight;  // ⚠️ змусити браузер застосувати висоту 0 перед переходом
    el.style.transition = `height ${duration}ms ease, opacity ${duration}ms ease`;
    el.style.height = height;
    el.style.opacity = '1';
    // 💡 після завершення прибираємо inline-стилі
    setTimeout(() => {
      el.style.removeProperty('height');
      el.style.removeProperty('overflow');
      el.style.removeProperty('transition');
    }, duration);
  }
};

function checkChartType() {
  const img1 = chart_type_btn.dataset.img1;
  const img2 = chart_type_btn.dataset.img2;
  const state = chart_type_btn.dataset.state;
  const visibleChart = document.getElementsByClassName("visibleChart")[0]

  if (state === "1") {
    chart_type_btn.src = img2
    chart_type_btn.dataset.state = "2"
    visibleChart.id = 'timeTable'
  } else {
    chart_type_btn.src = img1
    chart_type_btn.dataset.state = "1"
    visibleChart.id = 'appUsage'
  }
  localStorage.setItem('chartType', visibleChart.id)
}

function renderVisibleChart(selectedPeriod) {
  const state = chart_type_btn.dataset.state;
  if (state === "1") {
    renderTotalAppTime(selectedPeriod);
  } else {
    renderTimeTable(selectedPeriod);
  }
}

function getSelectedPeriodFromStorage() {
  const savedPeriod = localStorage.getItem('selectedPeriod') || 'today_btn';
  const btn = document.querySelector(`#${savedPeriod}`);
  if (btn) btn.classList.add('active');
  const selectedPeriod = btn.id.replace('_btn', '');
  return selectedPeriod
}


//date-picker
function setupDateScroll(elem, min, max) {
  let startY = 0;
  let currentValue = parseInt(elem.textContent);
  let dragging = false;

  function updateValue(diff) {
    let step = Math.round(diff / 20); // чутливість
    let newValue = (currentValue - step);

    // Обмеження значень
    if (newValue < min) newValue = max;
    if (newValue > max) newValue = min;

    elem.textContent = String(newValue).padStart(2, "0");
  }

  // Wheel scroll (PC)
  elem.addEventListener("wheel", (e) => {
    e.preventDefault();
    currentValue = parseInt(elem.textContent);
    let delta = -Math.sign(e.deltaY);
    let newValue = currentValue + delta;

    // Обмеження значень
    if (newValue < min) newValue = max;
    if (newValue > max) newValue = min;

    elem.textContent = String(newValue).padStart(2, "0");
  }, { passive: false });

  // Mobile
  elem.addEventListener("touchstart", (e) => {
    startY = e.touches[0].clientY;
    dragging = true;
    currentValue = parseInt(elem.textContent);

    const moveHandler = (e) => {
      if (!dragging) return;
      let diff = e.touches[0].clientY - startY;
      updateValue(diff);
    };

    const upHandler = () => {
      dragging = false;
      document.removeEventListener("touchmove", moveHandler);
      document.removeEventListener("touchend", upHandler);
    };

    document.addEventListener("touchmove", moveHandler);
    document.addEventListener("touchend", upHandler);
  });
}

// Ініціалізація з поточною датою
function initializeDatePicker() {
  const date = new Date(localStorage.getItem('customDate')) || new Date();
  document.getElementById("year").textContent = date.getFullYear();
  document.getElementById("month").textContent = String(date.getMonth() + 1).padStart(2, "0");
  document.getElementById("day").textContent = String(date.getDate()).padStart(2, "0");
}
// Функція для отримання вибраної дати
function getSelectedDate() {
  const year = document.getElementById("year").textContent;
  const month = document.getElementById("month").textContent;
  const day = document.getElementById("day").textContent;
  return `${year}-${month}-${day}`;
}

// Налаштування обмежень для кожного поля
window.addEventListener('DOMContentLoaded', () => {
  initializeDatePicker();
  setupDateScroll(document.getElementById("year"), 2000, 2030);  // діапазон років
  setupDateScroll(document.getElementById("month"), 1, 12);      // місяці
  setupDateScroll(document.getElementById("day"), 1, 31);        // дні
});


window.addEventListener('DOMContentLoaded', () => {
  let selectedPeriod = getSelectedPeriodFromStorage();
  selectedPeriod = ('custom' == selectedPeriod) ? getSelectedDate() : selectedPeriod
  // Відновлюємо chartType з localStorage
  const chartType = localStorage.getItem('chartType') || 'appUsage';
  const visibleChart = document.getElementsByClassName("visibleChart")[0];
  visibleChart.id = chartType;
  // Відновлюємо стан кнопки
  if (chartType === 'appUsage') {
    chart_type_btn.dataset.state = "1";
    chart_type_btn.src = chart_type_btn.dataset.img1;
  } else {
    chart_type_btn.dataset.state = "2";
    chart_type_btn.src = chart_type_btn.dataset.img2;
  }
  renderTotalLine(selectedPeriod);
  renderVisibleChart(selectedPeriod);
});

chart_type_btn.addEventListener("click", (event) => {
  let selectedPeriod = getSelectedPeriodFromStorage();
  selectedPeriod = ('custom' == selectedPeriod) ? getSelectedDate() : selectedPeriod
  checkChartType(event)
  renderVisibleChart(selectedPeriod)
});


const date_picker = document.getElementsByClassName('date-picker')[0]
date_picker.addEventListener('click', () => {
  const selectedPeriod = getSelectedDate()
  localStorage.setItem('selectedPeriod', 'custom_btn');
  localStorage.setItem('customDate', selectedPeriod);
  renderTotalLine(selectedPeriod);
  renderVisibleChart(selectedPeriod);
})

periodButtons.forEach(id => {
  document.getElementById(id).addEventListener('click', choosePeriod);
});
