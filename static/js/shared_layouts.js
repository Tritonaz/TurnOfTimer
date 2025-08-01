// Функція для перетворення секунд у "dd hh:mm:ss"
function secondsToDhms(seconds) {
    const d = Math.floor(seconds / (3600 * 24));
    const h = Math.floor((seconds % (3600 * 24)) / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = Math.round(seconds % 60);
    return `${d}d ${h}h ${m}m ${s}s`;
  }
  

// Функція, яка виконує reload тільки один раз на вхід мишки
// let canRefresh = true;

// Коли мишка заходить у вікно
// window.addEventListener('mouseover', () => {
//   if (canRefresh) {
//     location.reload();
//     canRefresh = false;
//   }
// });

// // Коли мишка повністю покидає вікно — дозволяємо оновлення знову
// window.addEventListener('mouseout', (e) => {
//   // Якщо мишка покинула вікно повністю
//   if (!e.relatedTarget && !e.toElement) {
//     canRefresh = true;
//   }
// });