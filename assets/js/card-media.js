/* Card videos play only while they are on screen, and never when the visitor
   prefers reduced motion (the poster frame stays instead). */
(function () {
  var vids = document.querySelectorAll('video.pc-media');
  if (!vids.length) return;

  if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

  if (!('IntersectionObserver' in window)) {
    vids.forEach(function (v) { v.play().catch(function () {}); });
    return;
  }

  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      var v = e.target;
      if (e.isIntersecting) {
        // Only fetch the video itself once the card is actually in view.
        if (v.preload !== 'auto') v.preload = 'auto';
        v.play().catch(function () {});
      } else {
        v.pause();
      }
    });
  }, { threshold: 0.25 });

  vids.forEach(function (v) { io.observe(v); });
})();
