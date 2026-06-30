document.addEventListener("DOMContentLoaded", () => {
  const autoSubmitForm = document.querySelector("[data-auto-submit]");
  if (autoSubmitForm instanceof HTMLFormElement) {
    window.setTimeout(() => autoSubmitForm.submit(), 900);
  }

  document.querySelectorAll("[data-chart-value]").forEach((bar) => {
    const value = Number(bar.getAttribute("data-chart-value"));
    const max = Number(bar.getAttribute("data-chart-max"));
    const height = max > 0 ? Math.max(18, Math.round((value / max) * 100)) : 18;
    bar.style.setProperty("--height", `${height}%`);
  });
});
