/* Mobile toggle for the global nav on standalone pages.

   The Webflow pages get this from jQuery plus four webflow.schunk.* files.
   All that is needed here is: show the panel, keep aria-expanded honest, and
   give people a way out that is not the button itself. */
(function () {
  var btn = document.querySelector('.menu-button-4');
  var menu = document.getElementById('site-nav-menu');
  if (!btn || !menu) return;

  var mq = window.matchMedia('(max-width: 991px)');

  function setOpen(open) {
    menu.hidden = !open;
    btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    btn.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
  }

  function sync() {
    // Above the breakpoint the panel is the ordinary row, so the hidden
    // attribute has to come off or the links vanish on resize.
    if (mq.matches) setOpen(false);
    else { menu.hidden = false; btn.setAttribute('aria-expanded', 'false'); }
  }

  btn.addEventListener('click', function () {
    setOpen(menu.hidden);
  });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && mq.matches && !menu.hidden) { setOpen(false); btn.focus(); }
  });

  // Following a link should close the panel, including an in-page anchor,
  // which does not reload and so would otherwise leave it covering the page.
  menu.addEventListener('click', function (e) {
    if (e.target.closest('a') && mq.matches) setOpen(false);
  });

  mq.addEventListener('change', sync);
  sync();
})();
