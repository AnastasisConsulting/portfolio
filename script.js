/**
 * G-YNTHETIC LABS // INTERFACE CONTROLLER
 * Premium interactions & scroll-driven dynamics
 */

(function () {
    'use strict';

    // ============================================================
    // SCROLL PROGRESS BAR
    // ============================================================
    const progressBar = document.createElement('div');
    progressBar.className = 'scroll-progress';
    document.body.prepend(progressBar);

    // ============================================================
    // STICKY NAV — appears after scrolling past header
    // ============================================================
    const nav = document.createElement('nav');
    nav.className = 'site-nav';
    nav.innerHTML = `
    <div class="nav-logo" style="white-space: nowrap;">G-YNTHETIC LABS</div>
    <ul class="nav-links">
      <li><a href="#vision">Foundation</a></li>
      <li><a href="#core-tech">Projects</a></li>
      <li><a href="#research">Research</a></li>
      <li><a href="#cognition">Architecture</a></li>
      <li><a href="#ai-problems">Problem Space</a></li>
      <li><a href="#business">Economics</a></li>
    </ul>
  `;
    document.body.prepend(nav);

    // ============================================================
    // INTERSECTION OBSERVER — Staggered reveals
    // ============================================================
    const revealObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('active');
                revealObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.08, rootMargin: '0px 0px -40px 0px' });

    // Section glow observer
    const glowObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            entry.target.classList.toggle('has-glow', entry.isIntersecting);
        });
    }, { threshold: 0.3 });

    // ============================================================
    // ANIMATED METRIC COUNTERS
    // ============================================================
    function animateCounter(el, target, duration = 1800) {
        const start = performance.now();
        const isInteger = Number.isInteger(target);

        function tick(now) {
            const elapsed = now - start;
            const progress = Math.min(elapsed / duration, 1);
            // Ease-out expo
            const eased = 1 - Math.pow(1 - progress, 4);
            const current = Math.round(eased * target);
            el.textContent = isInteger ? current.toLocaleString() : current;
            if (progress < 1) requestAnimationFrame(tick);
        }
        requestAnimationFrame(tick);
    }

    const metricObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting && !entry.target.dataset.counted) {
                entry.target.dataset.counted = 'true';
                const target = parseInt(entry.target.dataset.target, 10);
                if (!isNaN(target)) animateCounter(entry.target, target);
            }
        });
    }, { threshold: 0.5 });

    // ============================================================
    // MOUSE-TRACKING CARD GLOW
    // ============================================================
    function initCardGlow() {
        const cards = document.querySelectorAll('.card');
        cards.forEach(card => {
            card.addEventListener('mousemove', (e) => {
                const rect = card.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                card.style.setProperty('--glow-x', `${x}px`);
                card.style.setProperty('--glow-y', `${y}px`);
                card.style.setProperty('--glow-opacity', '1');
            });
            card.addEventListener('mouseleave', () => {
                card.style.setProperty('--glow-opacity', '0');
            });
        });
    }

    // Inject the glow layer CSS dynamically (keeps styles.css clean)
    const glowStyle = document.createElement('style');
    glowStyle.textContent = `
    .card {
      --glow-x: 50%;
      --glow-y: 50%;
      --glow-opacity: 0;
    }
    .card::before {
      content: '';
      position: absolute;
      top: 0; left: 0; right: 0; bottom: 0;
      background: radial-gradient(
        300px circle at var(--glow-x) var(--glow-y),
        rgba(0, 228, 245, 0.06),
        transparent 70%
      );
      opacity: var(--glow-opacity);
      transition: opacity 0.4s ease;
      pointer-events: none;
      z-index: 0;
    }
    .card > * { position: relative; z-index: 1; }
  `;
    document.head.appendChild(glowStyle);

    // ============================================================
    // PROBLEM COLUMN HOVER PULSE
    // ============================================================
    function initProblemPulse() {
        const cols = document.querySelectorAll('.problem-col');
        cols.forEach(col => {
            col.addEventListener('mouseenter', () => {
                col.style.borderColor = 'var(--accent-cyan)';
                col.style.background = 'var(--accent-cyan-dim)';
            });
            col.addEventListener('mouseleave', () => {
                col.style.borderColor = '';
                col.style.background = '';
            });
        });
    }

    // ============================================================
    // SCROLL HANDLER — progress bar + sticky nav
    // ============================================================
    let ticking = false;
    const header = document.querySelector('header');
    const headerHeight = header ? header.offsetHeight : 500;

    function onScroll() {
        if (!ticking) {
            requestAnimationFrame(() => {
                const scrollY = window.scrollY;
                const docHeight = document.documentElement.scrollHeight - window.innerHeight;
                const progress = docHeight > 0 ? (scrollY / docHeight) * 100 : 0;

                // Update progress bar width
                progressBar.style.width = progress + '%';

                // Toggle nav visibility
                nav.classList.toggle('visible', scrollY > headerHeight * 0.6);

                ticking = false;
            });
            ticking = true;
        }
    }

    window.addEventListener('scroll', onScroll, { passive: true });

    // ============================================================
    // SMOOTH SCROLL for anchor links
    // ============================================================
    document.addEventListener('click', (e) => {
        const anchor = e.target.closest('a[href^="#"]');
        if (!anchor) return;
        e.preventDefault();
        const target = document.querySelector(anchor.getAttribute('href'));
        if (target) {
            target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    });

    // ============================================================
    // STEALTH VISITOR COUNTER — Secret key 'GLABS'
    // ============================================================
    const COUNTER_KEY = 'gynthetic_labs_v5';
    let keyBuffer = '';

    // Hidden Hit Request
    async function trackVisit() {
        try {
            // Using a simple public counter API (CounterAPI.dev)
            await fetch(`https://api.counterapi.dev/v1/gynthetic-labs/visits/up`);
        } catch (e) {
            console.error('Telemetry offline');
        }
    }

    async function getVisitCount() {
        try {
            const res = await fetch(`https://api.counterapi.dev/v1/gynthetic-labs/visits`);
            const data = await res.json();
            return data.count || 'ERR';
        } catch (e) {
            return 'OFFLINE';
        }
    }

    function showAdminDashboard(count) {
        let dashboard = document.getElementById('admin-dash');
        if (!dashboard) {
            dashboard = document.createElement('div');
            dashboard.id = 'admin-dash';
            Object.assign(dashboard.style, {
                position: 'fixed',
                bottom: '20px',
                right: '20px',
                background: '#060608',
                border: '1px solid #00e4f5',
                padding: '1.5rem',
                zIndex: '10001',
                fontFamily: 'JetBrains Mono, monospace',
                fontSize: '0.8rem',
                color: '#00e4f5',
                boxShadow: '0 0 20px rgba(0, 228, 245, 0.2)',
                display: 'none'
            });
            document.body.appendChild(dashboard);
        }

        dashboard.innerHTML = `
            <div style="border-bottom: 1px solid rgba(0,228,245,0.2); margin-bottom: 1rem; padding-bottom: 0.5rem; font-weight: bold;">[ SYSTEM DIAGNOSTICS ]</div>
            <div>STATUS: <span style="color: #84cc16">OPERATIONAL</span></div>
            <div style="margin-top: 0.5rem;">TOTAL VISITORS: <span style="font-size: 1.2rem;">${count}</span></div>
            <div style="margin-top: 1rem; font-size: 0.6rem; color: #8a8a96;">ESC TO CLOSE</div>
        `;
        dashboard.style.display = 'block';
    }

    document.addEventListener('keydown', async (e) => {
        if (e.key === 'Escape') {
            const dash = document.getElementById('admin-dash');
            if (dash) dash.style.display = 'none';
        }

        keyBuffer += e.key.toUpperCase();
        if (keyBuffer.length > 5) keyBuffer = keyBuffer.slice(-5);

        if (keyBuffer === 'GLABS') {
            const count = await getVisitCount();
            showAdminDashboard(count);
            keyBuffer = '';
        }
    });

    // ============================================================
    // INIT
    // ============================================================
    document.addEventListener('DOMContentLoaded', () => {
        // Track unique visit
        trackVisit();

        // Reveal animations
        document.querySelectorAll('.reveal').forEach(el => revealObserver.observe(el));


        // Section glow
        document.querySelectorAll('section').forEach(el => glowObserver.observe(el));

        // Metric counters
        document.querySelectorAll('.metric[data-target]').forEach(el => metricObserver.observe(el));

        // Card glow
        initCardGlow();

        // Problem pulse
        initProblemPulse();

        // Initial scroll state
        onScroll();

        // Console branding
        console.log(
            '%c ◆ G-YNTHETIC LABS — INTERFACE ONLINE ',
            'background: #060608; color: #00e4f5; font-weight: 500; border: 1px solid rgba(0,228,245,0.3); padding: 6px 12px; font-family: monospace;'
        );
    });

    // ============================================================
    // HEADER PARALLAX — subtle depth on mouse
    // ============================================================
    if (header) {
        header.addEventListener('mousemove', (e) => {
            const x = (e.clientX / window.innerWidth - 0.5) * 10;
            const y = (e.clientY / window.innerHeight - 0.5) * 10;
            header.style.backgroundPosition = `${x}px ${y}px`;
        });
    }

})();
