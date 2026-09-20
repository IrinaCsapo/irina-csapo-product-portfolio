/* Copies the email address to the clipboard and shows "Copied" above the
   button. Without JavaScript the link still opens the visitor's mail app. */
(function () {
  function flash(wrap) {
    wrap.classList.add('is-copied');
    clearTimeout(wrap._t);
    wrap._t = setTimeout(function () { wrap.classList.remove('is-copied'); }, 2200);
  }

  function legacyCopy(text) {
    var ta = document.createElement('textarea');
    ta.value = text;
    ta.setAttribute('readonly', '');
    ta.style.cssText = 'position:absolute;left:-9999px;top:0';
    document.body.appendChild(ta);
    ta.select();
    var ok = false;
    try { ok = document.execCommand('copy'); } catch (e) { ok = false; }
    document.body.removeChild(ta);
    return ok;
  }

  document.querySelectorAll('.copy-email').forEach(function (btn) {
    btn.addEventListener('click', function (e) {
      var email = btn.getAttribute('data-email');
      var wrap = btn.closest('.copy-email-wrap');
      if (!email || !wrap) return;           // fall back to the mailto link
      if (navigator.clipboard && navigator.clipboard.writeText) {
        e.preventDefault();
        navigator.clipboard.writeText(email).then(function () {
          flash(wrap);
        }, function () {
          if (legacyCopy(email)) flash(wrap);
          else window.location.href = btn.getAttribute('href');
        });
      } else if (legacyCopy(email)) {
        e.preventDefault();
        flash(wrap);
      }
    });
  });
})();
