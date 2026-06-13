/* ============================================================
   Portfolio motion — GSAP-driven.
   Locked to EXPRESSIVE on the main site (body class). The
   /preview-motion.html archive has no GSAP, so it falls back to
   the static path below and keeps its motion-level switch.
   ============================================================ */

(function () {
  const LEVELS = ['subtle', 'moderate', 'expressive'];
  const body = document.body;
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const switchBtns = Array.from(document.querySelectorAll('.motion-switch button'));

  // --- Motion-level switch (only present on the preview/archive page) ---
  function setLevel(level, persist) {
    if (!LEVELS.includes(level)) level = 'expressive';
    LEVELS.forEach((l) => body.classList.remove('motion-' + l));
    body.classList.add('motion-' + level);
    switchBtns.forEach((b) => b.classList.toggle('is-active', b.dataset.motion === level));
    if (persist) { try { localStorage.setItem('motionLevel', level); } catch (_) {} }
  }
  switchBtns.forEach((b) => b.addEventListener('click', () => setLevel(b.dataset.motion, true)));
  if (switchBtns.length) {
    let start = LEVELS.find((l) => body.classList.contains('motion-' + l));
    if (!start) { try { start = localStorage.getItem('motionLevel'); } catch (_) {} }
    setLevel(start || 'subtle', false);
  }

  const showAll = () => document.querySelectorAll('.reveal').forEach((e) => e.classList.add('is-visible'));

  // No GSAP (preview page) or reduced motion -> render everything statically.
  if (reduce || !window.gsap) { showAll(); return; }

  const gsap = window.gsap;
  gsap.registerPlugin(ScrollTrigger, MotionPathPlugin);
  body.classList.add('js-anim'); // disables CSS reveal transitions so GSAP owns motion

  // Start hidden (inline overrides any CSS), then animate in.
  gsap.set('.reveal', { opacity: 0, y: 26 });

  // --- Hero entrance ---
  gsap.timeline({ delay: 0.15 }).to(gsap.utils.toArray('.hero .reveal'), {
    opacity: 1, y: 0, duration: 0.7, stagger: 0.1, ease: 'power3.out',
  });

  // --- Section reveals on scroll ---
  gsap.utils.toArray('main > section:not(.hero)').forEach((sec) => {
    gsap.to(sec.querySelectorAll('.reveal'), {
      opacity: 1, y: 0, duration: 0.6, stagger: 0.08, ease: 'power3.out',
      scrollTrigger: { trigger: sec, start: 'top 82%' },
    });
  });

  // --- Aurora parallax ---
  const aurora = document.querySelector('[data-aurora]');
  if (aurora) {
    gsap.to(aurora, {
      yPercent: 35, ease: 'none',
      scrollTrigger: { trigger: '.hero', start: 'top top', end: 'bottom top', scrub: true },
    });
  }

  // --- Data pipeline: flowing connectors + packets + hub pulse ---
  const svg = document.querySelector('.pipeline svg');
  if (svg) {
    gsap.to('.pl-line', { strokeDashoffset: -28, duration: 1.1, repeat: -1, ease: 'none' });

    const flows = [
      { path: '#p1', dur: 2.0, n: 2 },
      { path: '#p2', dur: 1.7, n: 2 },
      { path: '#p3', dur: 2.0, n: 2 },
      { path: '#p4', dur: 1.5, n: 2 },
    ];
    flows.forEach((f, fi) => {
      for (let k = 0; k < f.n; k++) {
        const c = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        c.setAttribute('r', '4.5');
        c.setAttribute('class', 'pl-packet');
        svg.appendChild(c);
        gsap.to(c, {
          duration: f.dur, repeat: -1, ease: 'none', delay: (f.dur / f.n) * k + fi * 0.25,
          motionPath: { path: f.path, align: f.path, alignOrigin: [0.5, 0.5] },
        });
      }
    });

    const hubRect = svg.querySelector('.pl-hub rect');
    if (hubRect) {
      gsap.fromTo(hubRect, { attr: { 'stroke-opacity': 0.35 } },
        { attr: { 'stroke-opacity': 1 }, duration: 1.3, repeat: -1, yoyo: true, ease: 'sine.inOut' });
    }
  }

  // --- Magnetic primary buttons (pointer devices only) ---
  if (window.matchMedia('(pointer: fine)').matches) {
    document.querySelectorAll('.btn--primary').forEach((btn) => {
      btn.addEventListener('mousemove', (e) => {
        const r = btn.getBoundingClientRect();
        gsap.to(btn, {
          x: (e.clientX - r.left - r.width / 2) * 0.3,
          y: (e.clientY - r.top - r.height / 2) * 0.4,
          duration: 0.4, ease: 'power2.out',
        });
      });
      btn.addEventListener('mouseleave', () =>
        gsap.to(btn, { x: 0, y: 0, duration: 0.5, ease: 'elastic.out(1, 0.4)' }));
    });
  }

  window.addEventListener('load', () => ScrollTrigger.refresh());
})();
