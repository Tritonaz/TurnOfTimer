let isSleepMode = false;
let totalSeconds = 0;
let pollingInterval;

const updateDisplay = (seconds = totalSeconds) => {
  const hrs = String(Math.floor(seconds / 3600)).padStart(2, '0');
  const mins = String(Math.floor((seconds % 3600) / 60)).padStart(2, '0');
  const secs = String(seconds % 60).padStart(2, '0');

  document.getElementById('hours').textContent = hrs;
  document.getElementById('minutes').textContent = mins;
  document.getElementById('seconds').textContent = secs;
};

const updateTotalSecondsFromDisplay = () => {
  const hrs = parseInt(document.getElementById('hours').textContent);
  const mins = parseInt(document.getElementById('minutes').textContent);
  const secs = parseInt(document.getElementById('seconds').textContent);
  totalSeconds = hrs * 3600 + mins * 60 + secs;
};

const startTimer = () => {
  updateTotalSecondsFromDisplay();
  fetch('/start_timer', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      hours: Math.floor(totalSeconds / 3600),
      minutes: Math.floor((totalSeconds % 3600) / 60),
      seconds: totalSeconds % 60,
      mode: isSleepMode ? 'sleep' : 'shutdown'
    })
  }).then(() => {
    startPolling();
  });
};

const startPolling = () => {
  clearInterval(pollingInterval);
  pollingInterval = setInterval(() => {
    fetch('/get_time')
      .then(res => res.json())
      .then(data => {
        if (!data.running) {
          clearInterval(pollingInterval);
          pollingInterval = null;
          document.getElementById('startPauseIcon').src = '/static/images/play.png'; // resets icon
        }
        updateDisplay(data.remaining);
      });
  }, 1000);
};

const toggleTimer = () => {
  const icon = document.getElementById('startPauseIcon');
  if (pollingInterval) {
    clearInterval(pollingInterval);
    pollingInterval = null;
    fetch('/stop_timer', { method: 'POST' });
    icon.classList.remove('fade-in');
    icon.classList.add('fade-out');
    setTimeout(() => {
      icon.src = '/static/images/play.png';
      icon.classList.remove('fade-out');
      icon.classList.add('fade-in');
    }, 200);
  } else {
    icon.classList.remove('fade-in');
    icon.classList.add('fade-out');
    setTimeout(() => {
      icon.src = '/static/images/stop.png';
      icon.classList.remove('fade-out');
      icon.classList.add('fade-in');
    }, 200);
    startTimer();
  }
};

const toggleMode = () => {
  const btn = document.getElementById('modeBtn');
  isSleepMode = !isSleepMode;
  btn.classList.toggle('active', isSleepMode);

  fetch('/set_mode', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ mode: isSleepMode ? 'sleep' : 'shutdown' })
  });
};

const initializeTimer = () => {
  fetch('/get_time')
    .then(res => res.json())
    .then(data => {
      updateDisplay(data.remaining);
      if (data.mode == "sleep") {
        const btn = document.getElementById('modeBtn');
        // isSleepMode = !isSleepMode;
        // btn.classList.toggle('active', isSleepMode);
        isSleepMode = true;
        btn.classList.add('active');
      }
      if (data.running) {
        startPolling();
        document.getElementById('startPauseIcon').src = '/static/images/stop.png';
      }
    });
};

function setupDragScroll(elem, max) {
  let startY = 0;
  let currentValue = parseInt(elem.textContent);
  let dragging = false;

  function updateValue(diff) {
    let step = Math.round(diff / 20); // чутливість
    let newValue = (currentValue - step) % (max + 1);
    if (newValue < 0) newValue += max + 1;
    elem.textContent = String(newValue).padStart(2, "0");
  }

  // Wheel scroll (PC)
  elem.addEventListener("wheel", (e) => {
    if (pollingInterval) return; // 🚫 Блокуємо якщо таймер запущено
    e.preventDefault();
    currentValue = parseInt(elem.textContent);
    let delta = -Math.sign(e.deltaY);
    let newValue = (currentValue + delta) % (max + 1);
    if (newValue < 0) newValue += max + 1;
    elem.textContent = String(newValue).padStart(2, "0");
  }, { passive: false });

  // Mobile
  elem.addEventListener("touchstart", (e) => {
    if (pollingInterval) return; // 🚫 Блокуємо якщо таймер запущено
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

setupDragScroll(document.getElementById("hours"), 23);
setupDragScroll(document.getElementById("minutes"), 59);
setupDragScroll(document.getElementById("seconds"), 59);

window.addEventListener('DOMContentLoaded', initializeTimer);
document.getElementById('startPauseBtn').addEventListener('click', toggleTimer);
document.getElementById('modeBtn').addEventListener('click', toggleMode);
updateDisplay();
