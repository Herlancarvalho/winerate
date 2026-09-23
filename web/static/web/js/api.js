/* Utilitários compartilhados: fetch com CSRF, escape de HTML, estrelas e formatação. */
(function () {
  const cookie = (name) => {
    const hit = document.cookie.split("; ").find((c) => c.startsWith(name + "="));
    return hit ? decodeURIComponent(hit.split("=")[1]) : "";
  };

  class ApiError extends Error {
    constructor(status, data) {
      super((data && data.detail) || "Não foi possível concluir a operação.");
      this.status = status;
      this.data = data || {};
    }
  }

  async function api(path, { method = "GET", json, form } = {}) {
    const headers = { Accept: "application/json", "X-CSRFToken": cookie("csrftoken") };
    let body;
    if (json !== undefined) {
      headers["Content-Type"] = "application/json";
      body = JSON.stringify(json);
    } else if (form) {
      body = form; // multipart: o navegador define o boundary
    }
    const res = await fetch(path, { method, headers, body, credentials: "same-origin" });
    const data = res.status === 204 ? null : await res.json().catch(() => null);
    const isAuthRoute = path === "/api/login" || path === "/api/register";
    if (!res.ok) {
      // Sessão expirada: o DRF responde 403 "credenciais não fornecidas" (SessionAuthentication)
      const notAuthenticated =
        res.status === 401 || (res.status === 403 && data && /credenciais|credentials/i.test(data.detail || ""));
      if (notAuthenticated && !isAuthRoute) {
        window.location.href = "/login/?next=" + encodeURIComponent(location.pathname);
      }
      throw new ApiError(res.status, data);
    }
    return data;
  }

  const ESC = { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" };
  const esc = (v) => String(v ?? "").replace(/[&<>"']/g, (c) => ESC[c]);

  function stars(n) {
    const value = Math.round(Number(n) || 0);
    let html = "";
    for (let i = 1; i <= 5; i++) {
      html += `<i class="fa-solid fa-star ${i <= value ? "" : "off"}"></i>`;
    }
    return `<span class="stars" role="img" aria-label="${value} de 5 estrelas">${html}</span>`;
  }

  const fmtDate = (iso) => {
    if (!iso) return "";
    const [y, m, d] = iso.split("-").map(Number);
    return new Date(y, m - 1, d).toLocaleDateString("pt-BR");
  };
  const fmtPrice = (p) =>
    p === null || p === undefined || p === ""
      ? ""
      : Number(p).toLocaleString("pt-BR", { style: "currency", currency: "BRL" });

  function showAlert(box, message, kind = "danger") {
    box.className = `alert alert-${kind}`;
    box.textContent = message;
  }
  const hideAlert = (box) => box.classList.add("d-none");

  /* Mostra erros de validação da API nos campos com [data-error-for]. */
  function applyErrors(form, data, alertBox) {
    form.querySelectorAll(".is-invalid").forEach((el) => el.classList.remove("is-invalid"));
    form.querySelectorAll("[data-error-for]").forEach((el) => (el.textContent = ""));
    const general = [];
    Object.entries(data || {}).forEach(([field, msgs]) => {
      const list = Array.isArray(msgs) ? msgs : [msgs];
      const slot = form.querySelector(`[data-error-for="${field}"]`);
      if (slot) {
        slot.textContent = list.join(" ");
        const input = form.querySelector(`[name="${field}"]`);
        if (input) input.classList.add("is-invalid");
      } else {
        general.push(list.join(" "));
      }
    });
    if (general.length && alertBox) showAlert(alertBox, general.join(" "));
  }

  window.WR = { api, ApiError, esc, stars, fmtDate, fmtPrice, showAlert, hideAlert, applyErrors };
})();
