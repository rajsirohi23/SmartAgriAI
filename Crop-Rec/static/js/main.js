// document.addEventListener("DOMContentLoaded", () => {
//   const form = document.getElementById("crop-form");
//   if (!form) return;

//   form.addEventListener("submit", (event) => {
//     const inputs = form.querySelectorAll("input[required]");
//     let hasError = false;

//     inputs.forEach((input) => {
//       input.classList.remove("input-error");
//       if (!input.value.trim()) {
//         hasError = true;
//         input.classList.add("input-error");
//       }
//     });

//     if (hasError) {
//       event.preventDefault();
//       // Basic UX hint; main error messaging handled server-side
//       alert("Please fill in all required fields before submitting.");
//     }
//   });
// });



/* ================================================================
   SMART AGRICULTURE AI — script.js
   Handles: Canvas BG, Navbar, Reveal, Counter, Tilt, Scroll, Form
   ================================================================ */

/* ---------------------------------------------------------------
   1. ANIMATED CANVAS BACKGROUND (Particle Field + Grid)
--------------------------------------------------------------- */
(function initCanvas() {
  const canvas = document.getElementById('bgCanvas');
  const ctx    = canvas.getContext('2d');
  let W, H, particles = [], animId;

  // Resize canvas to window
  function resize() {
    W = canvas.width  = window.innerWidth;
    H = canvas.height = window.innerHeight;
  }

  // Particle constructor
  function Particle() {
    this.reset();
  }
  Particle.prototype.reset = function () {
    this.x  = Math.random() * W;
    this.y  = Math.random() * H;
    this.r  = Math.random() * 1.5 + 0.4;
    this.vx = (Math.random() - 0.5) * 0.3;
    this.vy = (Math.random() - 0.5) * 0.3;
    this.alpha = Math.random() * 0.5 + 0.1;
  };
  Particle.prototype.update = function () {
    this.x += this.vx;
    this.y += this.vy;
    if (this.x < 0 || this.x > W || this.y < 0 || this.y > H) this.reset();
  };
  Particle.prototype.draw = function () {
    ctx.beginPath();
    ctx.arc(this.x, this.y, this.r, 0, Math.PI * 2);
    ctx.fillStyle = `rgba(74, 222, 128, ${this.alpha})`;
    ctx.fill();
  };

  // Build particle array
  function buildParticles() {
    particles = [];
    const count = Math.floor((W * H) / 12000);
    for (let i = 0; i < count; i++) particles.push(new Particle());
  }

  // Draw subtle grid
  function drawGrid() {
    const size = 80;
    ctx.strokeStyle = 'rgba(74, 222, 128, 0.03)';
    ctx.lineWidth = 1;
    for (let x = 0; x < W; x += size) {
      ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, H); ctx.stroke();
    }
    for (let y = 0; y < H; y += size) {
      ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke();
    }
  }

  // Connect nearby particles with lines
  function connectParticles() {
    const maxDist = 120;
    for (let i = 0; i < particles.length; i++) {
      for (let j = i + 1; j < particles.length; j++) {
        const dx = particles[i].x - particles[j].x;
        const dy = particles[i].y - particles[j].y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < maxDist) {
          const alpha = (1 - dist / maxDist) * 0.15;
          ctx.strokeStyle = `rgba(74, 222, 128, ${alpha})`;
          ctx.lineWidth = 0.6;
          ctx.beginPath();
          ctx.moveTo(particles[i].x, particles[i].y);
          ctx.lineTo(particles[j].x, particles[j].y);
          ctx.stroke();
        }
      }
    }
  }

  // Main loop
  function animate() {
    animId = requestAnimationFrame(animate);
    ctx.clearRect(0, 0, W, H);
    drawGrid();
    connectParticles();
    particles.forEach(p => { p.update(); p.draw(); });
  }

  // Init
  resize();
  buildParticles();
  animate();

  window.addEventListener('resize', () => {
    cancelAnimationFrame(animId);
    resize();
    buildParticles();
    animate();
  });
})();


/* ---------------------------------------------------------------
   2. NAVBAR — scroll shrink + active link highlight
      Works on both index.html and sub-pages (crop.html etc.)
--------------------------------------------------------------- */
(function initNavbar() {
  const navbar   = document.getElementById('navbar');
  const links    = document.querySelectorAll('.nav-link');
  const sections = document.querySelectorAll('section[id]');
  const isSubPage = !sections.length; // true on crop.html etc.

  // Scroll handler
  window.addEventListener('scroll', () => {
    // Shrink navbar on scroll
    navbar.classList.toggle('scrolled', window.scrollY > 60);

    // Highlight active section link (only on pages with sections)
    if (!isSubPage) {
      let current = '';
      sections.forEach(sec => {
        if (window.scrollY >= sec.offsetTop - 100) current = sec.id;
      });
      links.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === '#' + current) {
          link.classList.add('active');
        }
      });
    }
  });

  // Smooth scroll for same-page anchor links (#section)
  links.forEach(link => {
    link.addEventListener('click', e => {
      const href = link.getAttribute('href');
      // Only intercept pure anchor links (not index.html#section cross-page links)
      if (href && href.startsWith('#')) {
        e.preventDefault();
        const el = document.querySelector(href);
        if (el) el.scrollIntoView({ behavior: 'smooth' });
        document.getElementById('navLinks').classList.remove('open');
      }
    });
  });
})();


/* ---------------------------------------------------------------
   3. HAMBURGER MENU (mobile)
--------------------------------------------------------------- */
(function initHamburger() {
  const ham   = document.getElementById('hamburger');
  const links = document.getElementById('navLinks');
  ham.addEventListener('click', () => links.classList.toggle('open'));
})();


/* ---------------------------------------------------------------
   4. SCROLL REVEAL ANIMATION
--------------------------------------------------------------- */
(function initReveal() {
  const items = document.querySelectorAll('.reveal');

  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry, idx) => {
      if (entry.isIntersecting) {
        // Stagger if inside a grid
        const delay = entry.target.dataset.delay || 0;
        setTimeout(() => {
          entry.target.classList.add('visible');
        }, Number(delay));
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12 });

  items.forEach(item => observer.observe(item));
})();


/* ---------------------------------------------------------------
   5. COUNTER ANIMATION (stats in hero)
--------------------------------------------------------------- */
(function initCounters() {
  const counters = document.querySelectorAll('.stat-num');
  let started = false;

  function startCounters() {
    if (started) return;
    started = true;
    counters.forEach(counter => {
      const target   = parseInt(counter.dataset.target);
      const duration = 2000; // ms
      const step     = target / (duration / 16);
      let current    = 0;
      const timer = setInterval(() => {
        current += step;
        if (current >= target) {
          counter.textContent = target.toLocaleString();
          clearInterval(timer);
        } else {
          counter.textContent = Math.floor(current).toLocaleString();
        }
      }, 16);
    });
  }

  // Trigger when hero stats enter view
  const statsBlock = document.querySelector('.hero-stats');
  if (statsBlock) {
    const obs = new IntersectionObserver(entries => {
      if (entries[0].isIntersecting) {
        startCounters();
        obs.disconnect();
      }
    }, { threshold: 0.5 });
    obs.observe(statsBlock);
  }
})();


/* ---------------------------------------------------------------
   6. CARD TILT EFFECT (3D parallax on hover)
--------------------------------------------------------------- */
(function initTilt() {
  const cards = document.querySelectorAll('.tilt-card');

  cards.forEach(card => {
    card.addEventListener('mousemove', e => {
      const rect   = card.getBoundingClientRect();
      const cx     = rect.left + rect.width  / 2;
      const cy     = rect.top  + rect.height / 2;
      const dx     = (e.clientX - cx) / (rect.width  / 2);
      const dy     = (e.clientY - cy) / (rect.height / 2);
      const tiltX  = dy * -6;  // max 6deg
      const tiltY  = dx *  6;
      card.style.transform = `perspective(800px) rotateX(${tiltX}deg) rotateY(${tiltY}deg) translateY(-6px)`;
    });

    card.addEventListener('mouseleave', () => {
      card.style.transform = '';
    });
  });
})();


/* ---------------------------------------------------------------
   7. CONTACT FORM — toast feedback
--------------------------------------------------------------- */
(function initForm() {
  const form  = document.getElementById('contactForm');
  const toast = document.getElementById('formToast');
  if (!form) return;

  form.addEventListener('submit', e => {
    e.preventDefault();
    // Show toast
    toast.classList.add('show');
    // Reset form
    form.reset();
    // Hide toast after 3.5s
    setTimeout(() => toast.classList.remove('show'), 3500);
  });
})();


/* ---------------------------------------------------------------
   8. FLOATING HERO CHIPS — subtle continuous float
   (CSS handles this via @keyframes chipFloat)
   Extra JS: mouse parallax on hero visual
--------------------------------------------------------------- */
(function initHeroParallax() {
  const visual = document.querySelector('.hero-visual');
  if (!visual) return;

  document.addEventListener('mousemove', e => {
    const cx = window.innerWidth  / 2;
    const cy = window.innerHeight / 2;
    const dx = (e.clientX - cx) / cx;
    const dy = (e.clientY - cy) / cy;
    visual.style.transform = `translate(${dx * 12}px, ${dy * 8}px)`;
  });
})();


/* ---------------------------------------------------------------
   9. SMOOTH ACTIVE NAV UNDERLINE on page load
--------------------------------------------------------------- */
(function setInitialActive() {
  const links = document.querySelectorAll('.nav-link');
  if (links.length) links[0].classList.add('active');
})();


/* ---------------------------------------------------------------
   10. FEATURE BOXES — staggered entry
--------------------------------------------------------------- */
(function staggerFeatureBoxes() {
  const boxes = document.querySelectorAll('.feature-box');
  boxes.forEach((box, i) => {
    box.style.transitionDelay = `${i * 80}ms`;
  });
})();