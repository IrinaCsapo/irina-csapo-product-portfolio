/* A friendly no-cookies note, bottom left. Dismissing it stores a single
   "dismissed" flag in localStorage (no cookie, no identifier) so it doesn't
   reappear on every page. Markup and styles live here so each page only
   needs this one script tag. */
(function () {
  var KEY = 'cookie-note-dismissed';
  try { if (localStorage.getItem(KEY)) return; } catch (e) { /* storage blocked: still show */ }

  var css = [
    '.cookie-note{position:fixed;left:24px;bottom:24px;z-index:9999;max-width:360px;',
    'display:flex;flex-direction:column;gap:14px;padding:20px 22px;border-radius:16px;',
    'background:#fff;color:#000645;box-shadow:0 18px 44px rgba(0,6,69,.16);',
    'font-family:"Albert Sans",sans-serif;font-size:16px;line-height:1.4;',
    'opacity:0;transform:translateY(16px);transition:opacity .45s ease,transform .45s ease}',
    '.cookie-note.is-in{opacity:1;transform:none}',
    '.cookie-note p{margin:0;color:#000645;font-size:16px;line-height:1.4;font-weight:400}',
    '.cookie-note strong{font-weight:700}',
    '.cookie-note button{align-self:flex-start;border:0;border-radius:999px;cursor:pointer;',
    'padding:11px 22px;background:#ff0091;color:#fff;font:700 15px "Albert Sans",sans-serif;',
    'transition:background .25s}',
    '.cookie-note button:hover{background:#000645}',
    '@media (max-width:767px){.cookie-note{left:12px;right:12px;bottom:12px;max-width:none;padding:18px}}',
    '@media (prefers-reduced-motion:reduce){.cookie-note{transition:none}}'
  ].join('');

  var style = document.createElement('style');
  style.textContent = css;
  document.head.appendChild(style);

  var note = document.createElement('div');
  note.className = 'cookie-note';
  note.setAttribute('role', 'region');
  note.setAttribute('aria-label', 'Cookie notice');
  note.innerHTML =
    '<p><strong>No cookies here.</strong> I actually don’t store any cookies, so I won’t be ' +
    'following you around. That’s a promise.</p>' +
    '<button type="button">Crumbs, thanks!</button>';
  document.body.appendChild(note);

  requestAnimationFrame(function () {
    setTimeout(function () { note.classList.add('is-in'); }, 700);
  });

  note.querySelector('button').addEventListener('click', function () {
    try { localStorage.setItem(KEY, '1'); } catch (e) {}
    note.classList.remove('is-in');
    setTimeout(function () { note.remove(); }, 450);
  });
})();
