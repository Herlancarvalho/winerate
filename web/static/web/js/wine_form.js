(function () {
  const { api, ApiError, showAlert, hideAlert, applyErrors } = window.WR;
  const $ = (id) => document.getElementById(id);
  const root = $("formRoot");
  const form = $("wineForm");
  const alertBox = $("alertBox");
  const wineId = root.dataset.wineId;
  const MAX_BYTES = 5 * 1024 * 1024;
  const AI_FIELDS = ["name", "winery", "vintage", "grape", "country", "region"];
  const TEXT_FIELDS = ["name", "winery", "country", "region", "grape", "location", "comment"];

  /* Data padrão = hoje (no fuso do usuário); futuro é bloqueado */
  const today = new Date(Date.now() - new Date().getTimezoneOffset() * 60000).toISOString().slice(0, 10);
  form.tasting_date.max = today;
  if (!wineId) form.tasting_date.value = today;

  /* ---------- Edição: carrega o vinho pela API (404 se não for do usuário) ---------- */
  async function loadWine() {
    try {
      const w = await api(`/api/wines/${wineId}`);
      [...TEXT_FIELDS, "vintage", "price", "tasting_date"].forEach((f) => {
        if (form[f]) form[f].value = w[f] ?? "";
      });
      const radio = form.querySelector(`input[name=rating][value="${Number(w.rating)}"]`);
      if (radio) radio.checked = true;
    } catch (err) {
      form.classList.add("d-none");
      showAlert(alertBox, err.status === 404 ? "Vinho não encontrado." : "Não foi possível carregar o vinho.");
    }
  }
  if (wineId) loadWine();

  /* ---------- Rótulo: prévia + preenchimento assistido ---------- */
  if (!wineId) {
    const file = $("labelFile");
    const btn = $("btnIdentify");
    let previewUrl = null;

    file.addEventListener("change", () => {
      hideAlert(alertBox);
      if (previewUrl) URL.revokeObjectURL(previewUrl);
      const f = file.files[0];
      if (!f) { btn.disabled = true; $("previewBox").classList.add("d-none"); return; }
      if (f.size > MAX_BYTES) {
        showAlert(alertBox, "A imagem excede 5 MB. Escolha uma foto menor.");
        file.value = ""; btn.disabled = true; $("previewBox").classList.add("d-none");
        return;
      }
      previewUrl = URL.createObjectURL(f);
      $("preview").src = previewUrl;
      $("previewBox").classList.remove("d-none");
      btn.disabled = false;
    });

    btn.addEventListener("click", async () => {
      const f = file.files[0];
      if (!f) return;
      hideAlert(alertBox);
      btn.disabled = true;
      $("identifySpin").classList.remove("d-none");
      const notice = $("aiNotice");
      try {
        const fd = new FormData();
        fd.append("image", f);
        const res = await api("/api/wines/identify-label", { method: "POST", form: fd });
        let filled = 0;
        AI_FIELDS.forEach((name) => {
          const value = res.data[name];
          const input = form[name];
          if (value === null || value === "" || value === undefined || !input) return;
          input.value = value;
          input.classList.add("ai-filled");
          input.addEventListener("input", () => input.classList.remove("ai-filled"), { once: true });
          filled += 1;
        });
        notice.classList.remove("d-none");
        notice.textContent = filled
          ? "Campos sugeridos pela IA estão destacados. Revise, corrija o que for preciso e escolha a nota antes de salvar."
          : "Não consegui ler dados neste rótulo. Preencha manualmente ou tente outra foto.";
      } catch (err) {
        const msg = err instanceof ApiError && err.status === 429
          ? "Muitas leituras seguidas. Aguarde um instante."
          : (err.message || "Falha ao ler o rótulo.");
        showAlert(alertBox, msg);
      } finally {
        $("identifySpin").classList.add("d-none");
        btn.disabled = false;
      }
    });
  }

  /* ---------- Salvar (única forma de gravar: ação explícita do usuário) ---------- */
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    hideAlert(alertBox);
    const fd = new FormData(form);
    const payload = {};
    TEXT_FIELDS.forEach((f) => (payload[f] = (fd.get(f) || "").trim()));
    payload.vintage = fd.get("vintage") ? Number(fd.get("vintage")) : null;
    payload.price = fd.get("price") ? fd.get("price") : null;
    payload.tasting_date = fd.get("tasting_date") || null;
    payload.rating = fd.get("rating") ? Number(fd.get("rating")) : null;

    const errors = {};
    if (!payload.name) errors.name = ["Informe o nome do vinho."];
    if (!payload.rating) errors.rating = ["Escolha uma nota de 1 a 5."];
    if (!payload.tasting_date) errors.tasting_date = ["Informe a data da degustação."];
    if (Object.keys(errors).length) return applyErrors(form, errors, alertBox);
    applyErrors(form, {}, alertBox);

    const btn = $("btnSave");
    btn.disabled = true;
    $("saveSpin").classList.remove("d-none");
    try {
      await api(wineId ? `/api/wines/${wineId}` : "/api/wines", {
        method: wineId ? "PUT" : "POST",
        json: payload,
      });
      window.location.href = "/wines/";
    } catch (err) {
      if (err instanceof ApiError && err.status === 404) showAlert(alertBox, "Vinho não encontrado.");
      else if (err instanceof ApiError) applyErrors(form, err.data, alertBox);
      else showAlert(alertBox, "Falha de conexão. Tente novamente.");
      btn.disabled = false;
      $("saveSpin").classList.add("d-none");
    }
  });
})();
