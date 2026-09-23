(function () {
  const { api, ApiError, showAlert, hideAlert, applyErrors } = window.WR;
  const form = document.getElementById("authForm");
  const alertBox = document.getElementById("formAlert");
  const mode = form.dataset.mode;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    hideAlert(alertBox);
    const payload = Object.fromEntries(new FormData(form));
    const btn = form.querySelector("button[type=submit]");
    btn.disabled = true;
    try {
      await api(mode === "login" ? "/api/login" : "/api/register", { method: "POST", json: payload });
      const next = new URLSearchParams(location.search).get("next");
      // Só aceita caminhos internos, evitando redirecionamento aberto
      window.location.href = next && next.startsWith("/") && !next.startsWith("//") ? next : "/";
    } catch (err) {
      if (err instanceof ApiError) {
        applyErrors(form, err.data, alertBox);
        if (err.data && err.data.detail) showAlert(alertBox, err.data.detail);
        if (err.status === 429) showAlert(alertBox, "Muitas tentativas. Aguarde um instante e tente de novo.");
      } else {
        showAlert(alertBox, "Falha de conexão. Tente novamente.");
      }
      btn.disabled = false;
    }
  });
})();
