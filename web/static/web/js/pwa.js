/* Registro do service worker e convite para instalar o aplicativo. */
(function () {
  if ("serviceWorker" in navigator) {
    window.addEventListener("load", () => {
      navigator.serviceWorker.register("/sw.js", { scope: "/" }).catch(() => {});
    });
  }

  const banner = document.getElementById("installBanner");
  if (!banner) return;   // só aparece para quem está logado

  const KEY = "wr-install-dismissed";
  const SNOOZE_MS = 14 * 24 * 60 * 60 * 1000;   // não insistir por 14 dias

  const store = {
    get() { try { return Number(localStorage.getItem(KEY)) || 0; } catch (e) { return 0; } },
    set() { try { localStorage.setItem(KEY, String(Date.now())); } catch (e) { /* ignora */ } },
  };

  const isStandalone =
    window.matchMedia("(display-mode: standalone)").matches || window.navigator.standalone === true;
  const isIos = /iphone|ipad|ipod/i.test(navigator.userAgent) ||
    (navigator.platform === "MacIntel" && navigator.maxTouchPoints > 1);
  const snoozed = Date.now() - store.get() < SNOOZE_MS;

  if (isStandalone || snoozed) return;

  const btnInstall = document.getElementById("installBtn");
  const btnClose = document.getElementById("installClose");
  const hint = document.getElementById("installHint");
  const show = () => banner.classList.remove("d-none");
  const hide = () => banner.classList.add("d-none");

  btnClose.addEventListener("click", () => { store.set(); hide(); });

  /* Android / Chrome: o navegador avisa quando o app pode ser instalado */
  let deferred = null;
  window.addEventListener("beforeinstallprompt", (e) => {
    e.preventDefault();
    deferred = e;
    show();
  });
  btnInstall.addEventListener("click", async () => {
    if (!deferred) return;
    deferred.prompt();
    await deferred.userChoice;
    deferred = null;
    hide();
  });
  window.addEventListener("appinstalled", () => { store.set(); hide(); });

  /* iPhone / iPad: não existe botão de instalar, então mostramos o passo a passo */
  if (isIos) {
    hint.textContent = "Toque em Compartilhar (□↑) no Safari e depois em “Adicionar à Tela de Início”.";
    btnInstall.classList.add("d-none");
    btnClose.textContent = "Entendi";
    setTimeout(show, 2500);
  }
})();
