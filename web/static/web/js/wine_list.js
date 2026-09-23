(function () {
  const { api, esc, stars, fmtDate, fmtPrice, showAlert, hideAlert } = window.WR;
  const $ = (id) => document.getElementById(id);
  const form = $("filters");
  const modal = new bootstrap.Modal($("deleteModal"));
  let page = 1;
  let pendingDelete = null;
  let timer = null;

  function query() {
    const params = new URLSearchParams();
    new FormData(form).forEach((v, k) => v !== "" && params.set(k, v));
    params.set("page", page);
    return params.toString();
  }

  function card(w) {
    const meta = [w.winery, w.vintage, w.country, w.grape].filter(Boolean).map(esc).join(" · ");
    const price = fmtPrice(w.price);
    return `<div class="col-12 col-md-6 col-xl-4">
      <article class="wine-card">
        <div class="d-flex justify-content-between align-items-start gap-2">
          <h3>${esc(w.name)}</h3>${stars(w.rating)}
        </div>
        <div class="wine-meta">${meta || "&nbsp;"}</div>
        <div class="wine-meta"><i class="fa-regular fa-calendar me-1"></i>${fmtDate(w.tasting_date)}${price ? ` · ${esc(price)}` : ""}${w.location ? ` · ${esc(w.location)}` : ""}</div>
        ${w.comment ? `<p class="wine-comment mb-0">${esc(w.comment)}</p>` : ""}
        <div class="wine-actions">
          <a class="btn btn-sm btn-outline-wine" href="/wines/${Number(w.id)}/edit/"><i class="fa-solid fa-pen me-1"></i>Editar</a>
          <button class="btn btn-sm btn-outline-secondary" data-delete="${Number(w.id)}" data-name="${esc(w.name)}"><i class="fa-solid fa-trash me-1"></i>Excluir</button>
        </div>
      </article>
    </div>`;
  }

  async function load() {
    hideAlert($("alertBox"));
    $("loading").classList.remove("d-none");
    try {
      const data = await api(`/api/wines?${query()}`);
      $("list").innerHTML = data.results.map(card).join("");
      $("empty").classList.toggle("d-none", data.results.length > 0);
      const pages = Math.max(1, Math.ceil(data.count / 20));
      $("pager").classList.toggle("d-none", pages <= 1);
      $("pageInfo").textContent = `Página ${page} de ${pages} · ${data.count} vinhos`;
      $("prev").disabled = !data.previous;
      $("next").disabled = !data.next;
    } catch (err) {
      if (err.status === 404 && page > 1) { page -= 1; return load(); } // página deixou de existir
      showAlert($("alertBox"), "Não foi possível carregar seus vinhos.");
    } finally {
      $("loading").classList.add("d-none");
    }
  }

  const reload = (resetPage = true) => {
    if (resetPage) page = 1;
    load();
  };

  form.addEventListener("input", () => {           // filtros dinâmicos com debounce
    clearTimeout(timer);
    timer = setTimeout(reload, 300);
  });
  form.addEventListener("submit", (e) => e.preventDefault());
  form.addEventListener("reset", () => setTimeout(reload, 0));
  $("prev").addEventListener("click", () => { page -= 1; load(); });
  $("next").addEventListener("click", () => { page += 1; load(); });

  $("list").addEventListener("click", (e) => {
    const btn = e.target.closest("[data-delete]");
    if (!btn) return;
    pendingDelete = btn.dataset.delete;
    $("deleteName").textContent = btn.dataset.name;
    modal.show();
  });

  $("confirmDelete").addEventListener("click", async () => {
    if (!pendingDelete) return;
    const btn = $("confirmDelete");
    btn.disabled = true;
    try {
      await api(`/api/wines/${pendingDelete}`, { method: "DELETE" });
      modal.hide();
      reload(false);
    } catch (err) {
      modal.hide();
      showAlert($("alertBox"), "Não foi possível excluir o vinho.");
    } finally {
      btn.disabled = false;
      pendingDelete = null;
    }
  });

  load();
})();
