function triggerRipple(x, y) {
    const wrapper = document.createElement('div');
    wrapper.className = 'ripple-wrapper';
    wrapper.style.left = `${x}px`;
    wrapper.style.top = `${y}px`;

    for (let i = 0; i < 3; i++) {
        const ring = document.createElement('div');
        ring.className = 'ripple-ring';
        wrapper.appendChild(ring);
    }

    document.body.appendChild(wrapper);

    setTimeout(() => wrapper.remove(), 2000); // автоочищення
}




document.getElementById('blya_btn').addEventListener('click', function (e) {
    e.preventDefault();

    const spinner = document.getElementById('spinner');

    const rect = e.target.getBoundingClientRect();
    const x = rect.left + rect.width / 2;
    const y = rect.top + rect.height / 2;

    spinner.style.display = 'block'; // 🔄 Показати коло

    fetch('/blya', { method: 'POST' })
        .then(response => {
            if (response.ok) {
                spinner.style.display = 'none'; // 🛑 Сховати спінер
                triggerRipple(x, y);
            }
        });
});
