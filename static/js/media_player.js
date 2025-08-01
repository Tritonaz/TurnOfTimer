const barsContainer = document.getElementById("sound-bars");
const playerBox = document.getElementById("tablo");
const MAX_BARS = 16;
let peakHistory = [];
let currentPeak = 0;
let targetPeak = 0;
let frame = 0;

function getBarColor(peak) {
  if (peak > 0.9) return "#BA5DE0";     // Фіолетовий (дуже гучно)
  if (peak > 0.75) return "#A45DE0";    // Сливовий
  if (peak > 0.6) return "#83A5E0";     // Синьо-блакитний
  if (peak > 0.45) return "#5DE0BA";    // Бірюзовий
  if (peak > 0.3) return "#5DE07E";     // Зелений лайм
  if (peak > 0.15) return "#83E05D";    // Салатовий
  return "#B6E05D";                     // Жовто-зелений (тихо)
}

function updateTitle(data) {
  const titleEl = document.getElementById("track-title");
  const wrapper = document.getElementById("track-title-wrapper");
  titleEl.innerText = data.title;
  // Перевіримо після рендеру
  requestAnimationFrame(() => {
    if (titleEl.scrollWidth > wrapper.clientWidth) {
      titleEl.innerHTML = `<span>${data.title}</span><span>${data.title}</span>`;
      titleEl.classList.add("scrolling");
    } else {
      titleEl.innerText = data.title;
      titleEl.classList.remove("scrolling");
    }
  });
  document.getElementById("track-artist").innerText = data.artist;
  document.getElementById("track-source").innerText = data.source;
  document.getElementById("playback-status").innerText = data.playback_status ? '🟢' : '🟨';
}

function animateBars() {
  // Плавно наближаємося до targetPeak
  currentPeak += (targetPeak - currentPeak) * 0.1;
  updateBars(currentPeak);

  requestAnimationFrame(animateBars); // 60 FPS
}

function updateBars(peak) {
  frame++;
  if (frame % 8 !== 0) return;

  peakHistory.push(peak);
  if (peakHistory.length > MAX_BARS) peakHistory.shift();

  const maxHeight = 60;
  const fragment = document.createDocumentFragment();
  peakHistory.forEach(p => {
    const bar = document.createElement("div");
    bar.className = "bar";
    bar.style.width = `${100 / MAX_BARS - 0.5}%`;
    bar.style.height = `${p * maxHeight}px`;
    bar.style.backgroundColor = getBarColor(p);
    bar.style.borderRadius = "5px";
    fragment.appendChild(bar);
  });
  barsContainer.innerHTML = "";
  barsContainer.appendChild(fragment);

  const maxPeak = Math.max(...peakHistory)
  playerBox.style.boxShadow = `0px 0px 10px 6px #000000, 
                               0 0 15px 5px ${getBarColor(maxPeak)},
                               inset 0 0 20px 5px ${getBarColor(maxPeak)}`;
}

function animateBars() {
  currentPeak += (targetPeak - currentPeak) * 0.1;
  updateBars(currentPeak);
  requestAnimationFrame(animateBars);
}

let lastTitle = "";
let lastArtist = "";
let lastSource = "";
let lastPlaybackStatus = "";
let lastPeak = -1;

function updatePlayer(data) {
  const currentTitle = data.title;
  const currentArtist = data.artist;
  const currentSource = data.source;
  const currentPlaybackStatus = data.playback_status;
  // const currentPeak = data.peak;

  if (currentTitle != lastTitle || currentArtist != lastArtist || currentSource != lastSource || currentPlaybackStatus != lastPlaybackStatus) {
    lastTitle = currentTitle;
    lastArtist = currentArtist;
    lastSource = currentSource;
    lastSource = currentSource;
    lastPlaybackStatus = currentPlaybackStatus;
    updateTitle(data);
  };

  // if (currentPeak != lastPeak) {
  //   lastPeak = currentPeak;
  //   updateBars(currentPeak)
  // };
}

let barFrame = 0;
// Підключення до API Flask
async function fetchMediaInfo() {
  try {
    const res = await fetch("/media_info");
    const json = await res.json();
    targetPeak = json.peak;

    barFrame++;
    let basePeak = json.peak; // Базовий peak із сервера
    if (barFrame % 4 === 0) { basePeak *= 2; } // Кожен n-й "кадр" підсилюємо звук
    targetPeak = Math.min(basePeak, 1.0); // Клємимо до 1 (на всякий)

    updatePlayer(json);
  } catch (e) {
    console.error("Error fetching media info", e);
  }
}


function control_media(clickCount) {
  let chosen_btn = '';
  if (clickCount === 1) {
    chosen_btn = lastPlaybackStatus ? 'pause' : 'play';
  } else if (clickCount === 2) {
    chosen_btn = 'next'
  } else if (clickCount >= 3) {
    chosen_btn = 'previous'
  }
  fetch('/control_media', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ action: chosen_btn })
  });
};

let clickCount = 0;
let clickTimer;
document.getElementById('media-player').addEventListener('click', (e) => {
  clickCount++;
  if (clickTimer) clearTimeout(clickTimer);
  clickTimer = setTimeout(() => {
    control_media(clickCount)
    clickCount = 0; // скидаємо лічильник
  }, 250); // Час очікування між кліками (можна регулювати)
});

setInterval(fetchMediaInfo, 500);
animateBars();