function toggleTheme() {
    const body = document.getElementById("body");
    const icon = document.getElementById("themeIcon");

    body.classList.toggle("dark-mode");

    if (body.classList.contains("dark-mode")) {
        localStorage.setItem("theme", "dark");
        icon.innerHTML = "☀️";
    } else {
        localStorage.setItem("theme", "light");
        icon.innerHTML = "🌙";
    }
}

window.onload = function() {
    const savedTheme = localStorage.getItem("theme");
    const body = document.getElementById("body");
    const icon = document.getElementById("themeIcon");

    if (savedTheme === "dark") {
        body.classList.add("dark-mode");
        icon.innerHTML = "☀️";
    }
};
