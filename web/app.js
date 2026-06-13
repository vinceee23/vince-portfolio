/* ============================================================
   Portfolio motion controller
   - Three motion levels (subtle / moderate / expressive)
   - Toggled live via the floating pill; choice persists
   - This switcher is a TEMPORARY preview aid. Once Vince picks
     a level, hard-set document.body.className and delete the
     .motion-switch markup + this file's switcher wiring.
   ============================================================ */

(function () {
  const LEVELS = ['subtle', 'moderate', 'expressive'];
  const DEFAULT = 'subtle';
  const body = document.body;
  const buttons = Array.from(document.querySelectorAll('.motion-switch button'));
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // ---- Reveal-on-scroll ----
  const revealEls = Array.from(document.querySelectorAll('.reveal'));
  let io = null;

  function runReveals() {
    if (io) io.disconnect();
    revealEls.forEach((el) => el.classList.remove('is-visible'));
    // reflow so the transition replays
    void document.body.offsetWidth;
    io = new IntersectionObserver(
      (entries) => {
        entries.forEach((e) => {
          if (e.isIntersecting) {
            e.target.classList.add('is-visible');
            io.unobserve(e.target);
          }
        });
      },
      { threshold: 0.12 }
    );
    revealEls.forEach((el) => io.observe(el));
  }

  // ---- Parallax (moderate + expressive) ----
  const aurora = document.querySelector('[data-aurora]');
  const heroInner = document.querySelector('[data-hero-inner]');
  let factor = 0; // aurora parallax strength
  let heroFactor = 0; // hero content drift
  let ticking = false;

  function applyParallax() {
    const y = window.scrollY || 0;
    if (aurora) aurora.style.transform = factor ? `translate3d(0, ${y * factor}px, 0)` : '';
    if (heroInner) heroInner.style.transform = heroFactor ? `translate3d(0, ${y * heroFactor}px, 0)` : '';
    ticking = false;
  }
  function onScroll() {
    if (!ticking) {
      ticking = true;
      requestAnimationFrame(applyParallax);
    }
  }

  function setParallaxForLevel(level) {
    if (reduce) { factor = 0; heroFactor = 0; }
    else if (level === 'moderate') { factor = 0.32; heroFactor = 0; }
    else if (level === 'expressive') { factor = 0.55; heroFactor = -0.09; }
    else { factor = 0; heroFactor = 0; } // subtle
    applyParallax();
  }

  // ---- Level switching ----
  function setLevel(level, persist) {
    if (!LEVELS.includes(level)) level = DEFAULT;
    LEVELS.forEach((l) => body.classList.remove('motion-' + l));
    body.classList.add('motion-' + level);
    buttons.forEach((b) => b.classList.toggle('is-active', b.dataset.motion === level));
    setParallaxForLevel(level);
    runReveals();
    if (persist) {
      try { localStorage.setItem('motionLevel', level); } catch (_) {}
    }
  }

  buttons.forEach((b) => b.addEventListener('click', () => setLevel(b.dataset.motion, true)));
  window.addEventListener('scroll', onScroll, { passive: true });

  // ---- Init ----
  // Honor a hard-set body class first (index.html locks motion-expressive);
  // otherwise use a saved choice or the default (e.g. the preview page).
  let start = LEVELS.find(function (l) { return body.classList.contains('motion-' + l); });
  if (!start) {
    try { start = localStorage.getItem('motionLevel'); } catch (_) {}
  }
  setLevel(start || DEFAULT, false);
})();
