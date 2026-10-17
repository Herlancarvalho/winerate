(async function () {
  const { api, esc, stars, fmtDate, showAlert } = window.WR;
  const $ = (id) => document.getElementById(id);
  const PALETTE = ["#5c1226", "#7b1e3a", "#9c3f58", "#b86b7e", "#d4a0ae", "#8a7f80", "#3b0a1a", "#c9b8bb", "#6e4b53", "#a67c86"];

  function wineBlock(w) {
    if (!w) return "—";
    const sub = [w.winery, w.vintage].filter(Boolean).map(esc).join(" · ");
    return `<a class="text-decoration-none" href="/wines/${Number(w.id)}/edit/">${esc(w.name)}</a>
            ${sub ? `<div class="wine-meta">${sub}</div>` : ""}
            <div>${stars(w.rating)}</div>
            <div class="wine-meta">${fmtDate(w.tasting_date)}</div>`;
  }

  function goToWines(params) {
    location.href = "/wines/?" + new URLSearchParams(params).toString();
  }

  /* onSelect(label, index), quando informado, torna o gráfico clicável: tocar
     em uma barra/fatia leva para "Meus vinhos" já filtrado por aquela categoria. */
  function chart(canvasId, type, labels, data, options = {}, onSelect) {
    new Chart($(canvasId), {
      type,
      data: { labels, datasets: [{ data, backgroundColor: PALETTE, borderWidth: 0, borderRadius: type === "bar" ? 6 : 0 }] },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: type === "doughnut", position: "bottom" } },
        onHover: onSelect
          ? (evt, elements) => { evt.native.target.style.cursor = elements.length ? "pointer" : "default"; }
          : undefined,
        onClick: onSelect
          ? (evt, elements) => {
              if (!elements.length) return;
              const idx = elements[0].index;
              if (Number(data[idx]) === 0) return;   // nada cadastrado nessa fatia
              onSelect(labels[idx], idx);
            }
          : undefined,
        ...options,
      },
    });
  }

  try {
    const d = await api("/api/dashboard");
    $("loading").classList.add("d-none");
    if (!d.total_wines) return $("empty").classList.remove("d-none");

    $("content").classList.remove("d-none");
    $("statTotal").textContent = d.total_wines;
    $("statAvg").textContent = d.average_rating.toLocaleString("pt-BR", { minimumFractionDigits: 1, maximumFractionDigits: 2 });
    $("statAvgStars").innerHTML = stars(d.average_rating);
    $("statBest").innerHTML = wineBlock(d.best_wine);
    $("statLast").innerHTML = wineBlock(d.last_wine);

    const countryLabels = d.by_country.map((x) => x.label);
    const grapeLabels = d.by_grape.map((x) => x.label);

    const intAxis = { beginAtZero: true, ticks: { precision: 0 } };
    chart("chartCountry", "bar", countryLabels, d.by_country.map((x) => x.count), {
      indexAxis: "y", scales: { x: intAxis },
    }, (label) => goToWines({ country: label }));

    chart("chartGrape", "doughnut", grapeLabels, d.by_grape.map((x) => x.count), {}, (label) => goToWines({ grape: label }));

    chart("chartRating", "bar", d.by_rating.map((x) => `${x.rating} ★`), d.by_rating.map((x) => x.count), {
      scales: { y: intAxis },
    }, (_label, idx) => goToWines({ rating: d.by_rating[idx].rating }));

    const ratingAxis = { beginAtZero: true, max: 5, ticks: { stepSize: 1 } };
    chart("chartCountryAvg", "bar", countryLabels, d.by_country.map((x) => x.avg_rating), {
      indexAxis: "y", scales: { x: ratingAxis },
    }, (label) => goToWines({ country: label }));

    chart("chartGrapeAvg", "bar", grapeLabels, d.by_grape.map((x) => x.avg_rating), {
      scales: { y: ratingAxis },
    }, (label) => goToWines({ grape: label }));
  } catch (err) {
    $("loading").classList.add("d-none");
    showAlert($("alertBox"), "Não foi possível carregar o dashboard.");
  }
})();