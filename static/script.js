document.addEventListener("DOMContentLoaded", () => {
  const getStoredJson = (key) => {
    try {
      return JSON.parse(window.sessionStorage.getItem(key));
    } catch {
      return null;
    }
  };

  const setError = (message) => {
    const error = document.querySelector("[data-static-error]");
    if (!error) {
      return;
    }

    error.textContent = message;
    error.hidden = false;
  };

  const getUser = () => getStoredJson("energyUser");
  const getPredictionInput = () => getStoredJson("energyPredictionInput");

  const predictConsumption = (dateText, temperature, workingDay, devices) => {
    const date = new Date(`${dateText}T00:00:00`);
    const month = date.getMonth() + 1;
    const weekday = date.getDay();
    const weekdayLoad = workingDay ? 4.8 : 2.1;
    const temperatureLoad = Math.max(temperature - 18, 0) * 0.55;
    const deviceLoad = devices * 1.35;
    const seasonalLoad = (month % 6) * 0.7;
    const weekendAdjustment = weekday === 5 || weekday === 6 ? 1.5 : 0;
    const prediction = Number(
      (8.5 + weekdayLoad + temperatureLoad + deviceLoad + seasonalLoad + weekendAdjustment).toFixed(2),
    );
    const mae = Number(Math.max(prediction * 0.075, 1.2).toFixed(2));

    return {
      prediction,
      mae,
      chart: [
        Number((prediction * 0.72).toFixed(2)),
        Number((prediction * 0.86).toFixed(2)),
        Number((prediction * 0.94).toFixed(2)),
        prediction,
      ],
    };
  };

  document.querySelectorAll("[data-static-logout]").forEach((link) => {
    link.addEventListener("click", () => {
      window.sessionStorage.removeItem("energyUser");
      window.sessionStorage.removeItem("energyPredictionInput");
    });
  });

  if (document.body.hasAttribute("data-requires-static-login") && !getUser()) {
    window.location.href = "sc2.html";
    return;
  }

  const username = document.querySelector("[data-static-username]");
  if (username) {
    username.textContent = getUser()?.username || "";
  }

  const loginForm = document.querySelector("[data-static-login]");
  if (loginForm instanceof HTMLFormElement) {
    loginForm.addEventListener("submit", (event) => {
      event.preventDefault();
      const form = new FormData(loginForm);
      const usernameValue = String(form.get("username") || "").trim();
      const email = String(form.get("email") || "").trim();
      const password = String(form.get("password") || "");

      if (!usernameValue || !email.includes("@") || password.length < 6) {
        setError("أدخل اسم المستخدم وبريدا إلكترونيا صحيحا وكلمة مرور من 6 أحرف على الأقل.");
        return;
      }

      window.sessionStorage.setItem(
        "energyUser",
        JSON.stringify({ username: usernameValue, email }),
      );
      window.location.href = "sc3.html";
    });
  }

  const predictForm = document.querySelector("[data-static-predict]");
  if (predictForm instanceof HTMLFormElement) {
    predictForm.addEventListener("submit", (event) => {
      event.preventDefault();
      const form = new FormData(predictForm);
      const date = String(form.get("date") || "");
      const temperature = Number(form.get("temperature"));
      const workingDay = String(form.get("working_day") || "0") === "1";
      const devices = Number.parseInt(String(form.get("devices") || ""), 10);

      if (!date || Number.isNaN(temperature) || Number.isNaN(devices) || devices <= 0) {
        setError("أدخل قيما صحيحة للتاريخ ودرجة الحرارة وعدد الأجهزة.");
        return;
      }

      window.sessionStorage.setItem(
        "energyPredictionInput",
        JSON.stringify({ date, temperature, workingDay, devices }),
      );
      window.location.href = "sc4.html";
    });
  }

  if (document.body.hasAttribute("data-static-process")) {
    if (!getPredictionInput()) {
      window.location.href = "sc3.html";
      return;
    }

    window.setTimeout(() => {
      window.location.href = "sc5.html";
    }, 900);
  }

  if (document.body.hasAttribute("data-static-result")) {
    const input = getPredictionInput();
    if (!input) {
      window.location.href = "sc3.html";
      return;
    }

    const result = predictConsumption(input.date, input.temperature, input.workingDay, input.devices);
    const max = Math.max(...result.chart);
    const chart = document.querySelector("[data-static-chart]");

    document.querySelector("[data-result-prediction]").textContent = result.prediction;
    document.querySelector("[data-result-mae]").textContent = result.mae;
    document.querySelector("[data-result-date]").textContent = input.date;
    document.querySelector("[data-result-temperature]").textContent = `${input.temperature}°C`;
    document.querySelector("[data-result-working-day]").textContent = input.workingDay ? "نعم" : "لا";
    document.querySelector("[data-result-devices]").textContent = input.devices;

    if (chart) {
      chart.innerHTML = result.chart
        .map((value) => `<div class="bar" data-chart-value="${value}" data-chart-max="${max}"><span>${value}</span></div>`)
        .join("");
    }
  }

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
