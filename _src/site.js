(function(){
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* Analytics hook: event names only, never names, emails or answers */
  window.phmTrack = function(name){
    try { window.dispatchEvent(new CustomEvent('phm:track', {detail:{event:name}})); } catch(e){}
    if (window.dataLayer && window.dataLayer.push) window.dataLayer.push({event:name});
    if (typeof window.gtag === 'function') window.gtag('event', name);   /* GA4: event names only, never form answers */
  };
  document.addEventListener('click', function(e){
    var c = e.target.closest && e.target.closest('[data-consult]');
    if (c) window.phmTrack('consultation_request');
    var s = e.target.closest && e.target.closest('[data-service]');
    if (s){ try { sessionStorage.setItem('phm-service', s.getAttribute('data-service')); } catch(err){} window.phmTrack('consultation_request'); }
  });

  /* Current year in the footer */
  document.querySelectorAll('[data-year]').forEach(function(el){ el.textContent = String(new Date().getFullYear()); });

  /* Footer wordmark letters */
  document.querySelectorAll('.ftr .wordmark').forEach(function(el){
    var t = el.textContent; el.textContent = '';
    t.split('').forEach(function(c){ var s = document.createElement('span'); s.className = 'lt'; s.textContent = c === ' ' ? '\u00a0' : c; el.appendChild(s); });
  });

  /* Fit giant wordmarks to the full content width */
  var fits = document.querySelectorAll('[data-fit]');
  function fit(){
    fits.forEach(function(el){
      var cs = getComputedStyle(el.parentElement), w = el.parentElement.clientWidth - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight);
      el.style.fontSize = '100px';
      for (var k = 0; k < 3; k++){
        var nat = el.getBoundingClientRect().width;
        if (!nat) break;
        el.style.fontSize = (parseFloat(el.style.fontSize) * w / nat) + 'px';
      }
    });
  }
  fit();
  window.addEventListener('resize', fit);
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(fit);

  /* Header colours follow the section beneath it */
  var hdr = document.querySelector('.hdr');
  var themed = Array.prototype.slice.call(document.querySelectorAll('[data-theme], .scrub'));
  function headerTheme(){
    if (!hdr) return;
    var y = 46, dark = false;
    for (var i = 0; i < themed.length; i++){
      var r = themed[i].getBoundingClientRect();
      if (r.top <= y && r.bottom > y){
        dark = themed[i].classList.contains('scrub') ? themed[i].dataset.state !== 'light' : themed[i].getAttribute('data-theme') === 'dark';
      }
    }
    hdr.classList.toggle('on-dark', dark);
  }

  /* Background scrub: navy -> stone -> cream across a section */
  function hex(h){ h = h.replace('#',''); return [parseInt(h.slice(0,2),16), parseInt(h.slice(2,4),16), parseInt(h.slice(4,6),16)]; }
  var scrubs = Array.prototype.slice.call(document.querySelectorAll('.scrub')).map(function(s){
    return { el: s, stops: s.dataset.stops.split(',').map(hex), glow: s.querySelector('.dots.glow') };
  });
  function mix(stops, p){
    var seg = (stops.length - 1) * p, i = Math.min(stops.length - 2, Math.floor(seg)), t = seg - i;
    var a = stops[i], b = stops[i+1];
    return [0,1,2].map(function(k){ return Math.round(a[k] + (b[k] - a[k]) * t); });
  }
  function scrub(){
    var vh = window.innerHeight;
    scrubs.forEach(function(s){
      var r = s.el.getBoundingClientRect();
      var p = Math.min(1, Math.max(0, (vh * 0.5 - r.top) / (r.height)));
      if (reduce) p = 0;
      var c = mix(s.stops, p);
      s.el.style.backgroundColor = 'rgb(' + c.join(',') + ')';
      var light = (c[0]*0.299 + c[1]*0.587 + c[2]*0.114) > 150;
      s.el.dataset.state = light ? 'light' : 'dark';
      s.el.style.setProperty('--fg', light ? '#071A30' : '#F7EEE2');
      s.el.style.setProperty('--fg-dim', light ? 'rgba(7,26,48,.28)' : 'rgba(247,238,226,.32)');
      s.el.style.setProperty('--dot', light ? 'rgba(7,26,48,.2)' : 'rgba(247,238,226,.16)');
    });
  }
  scrubs.forEach(function(s){
    if (reduce || !s.glow) return;
    s.el.addEventListener('pointermove', function(e){
      var r = s.el.getBoundingClientRect();
      s.glow.style.setProperty('--mx', (e.clientX - r.left) + 'px');
      s.glow.style.setProperty('--my', (e.clientY - r.top) + 'px');
    });
  });

  /* Headline word load-in */
  document.querySelectorAll('[data-split],[data-splitv]').forEach(function(el){
    var i = 0;
    (function walk(node){
      Array.prototype.slice.call(node.childNodes).forEach(function(n){
        if (n.nodeType === 3){
          var f = document.createDocumentFragment();
          n.textContent.split(/(\s+)/).forEach(function(part){
            if (!part) return;
            if (/^\s+$/.test(part)){ f.appendChild(document.createTextNode(' ')); return; }
            var w = document.createElement('span'); w.className = 'w';
            var s = document.createElement('span'); s.textContent = part; s.style.setProperty('--i', i++);
            w.appendChild(s); f.appendChild(w);
          });
          n.parentNode.replaceChild(f, n);
        } else if (n.nodeType === 1) walk(n);
      });
    })(el);
    el.classList.add(el.hasAttribute('data-splitv') ? 'splitv' : 'split');
    if (!el.hasAttribute('data-splitv')) setTimeout(function(){ el.classList.add('done'); }, reduce ? 0 : 2200);
  });

  /* Scroll-lit words and characters */
  function splitInto(el, mode){
    var text = el.textContent.trim(); el.textContent = ''; el.setAttribute('aria-label', text);
    var parts = mode === 'chars' ? text.split('') : text.split(/\s+/);
    parts.forEach(function(p, k){
      var s = document.createElement('span'); s.className = mode === 'chars' ? 'ch' : 'lw'; s.textContent = p; s.setAttribute('aria-hidden','true');
      el.appendChild(s);
      if (mode !== 'chars' && k < parts.length - 1) el.appendChild(document.createTextNode(' '));
    });
    return el;
  }
  var lit = [];
  document.querySelectorAll('[data-words]').forEach(function(el){ lit.push(splitInto(el, 'words')); });
  document.querySelectorAll('[data-chars]').forEach(function(el){ lit.push(splitInto(el, 'chars')); });
  function light(){
    var vh = window.innerHeight;
    lit.forEach(function(el){
      var r = el.getBoundingClientRect();
      var p = reduce ? 1 : Math.min(1, Math.max(0, (vh * 0.82 - r.top) / (r.height + vh * 0.3)));
      var spans = el.children, n = Math.round(p * spans.length);
      for (var k = 0; k < spans.length; k++) spans[k].classList.toggle('lit', k < n);
    });
  }

  /* Three columns light up in turn as the section scrolls; hover takes over */
  var colSets = Array.prototype.slice.call(document.querySelectorAll('[data-cols]'));
  function cols(){
    var vh = window.innerHeight;
    colSets.forEach(function(set){
      if (set.dataset.hover === '1') return;
      var items = set.querySelectorAll('.col'), r = set.getBoundingClientRect();
      var p = reduce ? 1 : (vh * 0.75 - r.top) / (r.height * 0.9);
      var n = Math.max(0, Math.min(items.length, Math.floor(p * items.length) + 1));
      items.forEach(function(c, k){ c.classList.toggle('on', k < n); });
    });
  }
  colSets.forEach(function(set){
    set.querySelectorAll('.col').forEach(function(c){
      c.addEventListener('mouseenter', function(){ set.dataset.hover = '1'; set.querySelectorAll('.col').forEach(function(o){ o.classList.toggle('on', o === c); }); });
    });
    set.addEventListener('mouseleave', function(){ set.dataset.hover = ''; cols(); });
  });

  /* Services list: active item with image swap */
  document.querySelectorAll('[data-svclist]').forEach(function(box){
    var links = box.querySelectorAll('.list a'), pics = box.querySelectorAll('.pic > *'), cur = 0, timer = null;
    function set(i){ cur = i; links.forEach(function(a, k){ a.classList.toggle('on', k === i); }); pics.forEach(function(p, k){ p.classList.toggle('on', k === i); }); }
    links.forEach(function(a, k){
      a.addEventListener('mouseenter', function(){ stop(); set(k); });
      a.addEventListener('focus', function(){ stop(); set(k); });
    });
    function stop(){ if (timer){ clearInterval(timer); timer = null; } }
    set(0);
    if (!reduce) timer = setInterval(function(){ set((cur + 1) % links.length); }, 2600);
  });

  /* Back button: previous page on this site, otherwise Home */
  document.querySelectorAll('[data-back]').forEach(function(a){
    a.addEventListener('click', function(e){
      var ref = document.referrer, same = false;
      try { same = ref && new URL(ref).origin === location.origin && ref !== location.href; } catch(err){}
      if (same && history.length > 1){ e.preventDefault(); history.back(); }
    });
  });

  /* Mobile menu */
  var btn = document.querySelector('.menu-btn'), menu = document.getElementById('mobile-menu');
  function setMenu(open){
    btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    btn.querySelector('span').textContent = open ? 'Close' : 'Menu';
    menu.classList.toggle('open', open);
    if (open) menu.removeAttribute('inert'); else menu.setAttribute('inert', '');
    document.body.classList.toggle('menu-open', open);
    document.body.style.overflow = open ? 'hidden' : '';
    if (open){ var a = menu.querySelector('a'); if (a) a.focus(); }
  }
  if (btn && menu){
    btn.addEventListener('click', function(){ setMenu(btn.getAttribute('aria-expanded') !== 'true'); });
    document.addEventListener('keydown', function(e){ if (e.key === 'Escape' && menu.classList.contains('open')){ setMenu(false); btn.focus(); } });
    menu.addEventListener('click', function(e){ if (e.target.closest('a')) setMenu(false); });
    var mb = menu.querySelector('[data-menu-back]');
    if (mb) mb.addEventListener('click', function(){ setMenu(false); btn.focus(); });
  }

  /* Large logo at the top of the page, compact once scrolling */
  function setHdr(){ if (hdr) document.documentElement.style.setProperty('--hdr', hdr.offsetHeight + 'px'); }
  function logoSize(){ if (hdr){ hdr.classList.toggle('small', window.scrollY > 40); setHdr(); } }
  window.addEventListener('scroll', logoSize, {passive:true}); window.addEventListener('resize', setHdr); logoSize();
  if (hdr) hdr.addEventListener('transitionend', setHdr, true);

  var ticking = false;
  function onScroll(){
    if (ticking) return; ticking = true;
    requestAnimationFrame(function(){ scrub(); headerTheme(); light(); cols(); ticking = false; });
  }
  window.addEventListener('scroll', onScroll, {passive:true});
  window.addEventListener('resize', onScroll);
  scrub(); headerTheme(); light(); cols();

  /* Smooth scrolling (Lenis, when it loaded) */
  function initLenis(){ if (reduce || !window.Lenis || window.innerWidth < 900 || !window.matchMedia('(pointer: fine)').matches) return;
    try {
      var lenis = new window.Lenis({ duration: 1.15, smoothWheel: true }); window.__lenis = lenis;
      (function raf(t){ lenis.raf(t); requestAnimationFrame(raf); })(0);
      document.addEventListener('click', function(e){
        if (window.PHM_SINGLE) return;
        var a = e.target.closest && e.target.closest('a[href^="#"]');
        if (!a) return; var id = a.getAttribute('href'); if (id.length < 2) return;
        var t = document.querySelector(id); if (!t) return;
        e.preventDefault(); lenis.scrollTo(t, { offset: -((hdr ? hdr.offsetHeight : 90) + 16) });
      });
    } catch(err){}
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', initLenis); else initLenis();

  /* Cursor dot */
  if (!reduce && window.matchMedia('(pointer: fine)').matches){
    var cur = document.createElement('div'); cur.className = 'cur'; cur.setAttribute('aria-hidden','true'); document.body.appendChild(cur);
    var cx = -50, cy = -50, tx2 = -50, ty2 = -50;
    document.addEventListener('mousemove', function(e){ tx2 = e.clientX; ty2 = e.clientY; cur.classList.add('on'); });
    document.addEventListener('mouseleave', function(){ cur.classList.remove('on'); });
    document.addEventListener('mouseover', function(e){ cur.classList.toggle('big', !!(e.target.closest && e.target.closest('a,button,.media,.tcard,.col,select,label'))); });
    (function loop(){ cx += (tx2 - cx) * .2; cy += (ty2 - cy) * .2; cur.style.transform = 'translate(' + cx + 'px,' + cy + 'px)'; requestAnimationFrame(loop); })();
    document.querySelectorAll('.blk').forEach(function(b){
      b.addEventListener('mousemove', function(e){ var r = b.getBoundingClientRect(); b.style.transform = 'translate(' + ((e.clientX - r.left - r.width/2) * .2) + 'px,' + ((e.clientY - r.top - r.height/2) * .35) + 'px)'; });
      b.addEventListener('mouseleave', function(){ b.style.transform = ''; });
      b.style.transition = 'color .4s cubic-bezier(.22,1,.36,1), transform .5s cubic-bezier(.22,1,.36,1)';
    });
  }

  /* Marquee skews with scroll speed */
  var mqs = document.querySelectorAll('.mq-in'), lastY2 = window.scrollY, skewT = null;
  if (mqs.length && !reduce){
    window.addEventListener('scroll', function(){
      var v = Math.max(-12, Math.min(12, (window.scrollY - lastY2) * .25)); lastY2 = window.scrollY;
      mqs.forEach(function(m){ m.style.setProperty('--skew', (-v) + 'deg'); });
      clearTimeout(skewT); skewT = setTimeout(function(){ mqs.forEach(function(m){ m.style.setProperty('--skew', '0deg'); }); }, 120);
    }, {passive:true});
  }

  /* Night sky: dense faint stars, a few bright ones, natural colours */
  document.querySelectorAll('canvas.stars').forEach(function(cv){
    var ctx = cv.getContext('2d'); if (!ctx) return;
    var dpr = Math.min(window.devicePixelRatio || 1, 2), W, H, stars = [], vis = true, t0 = 0;
    var tints = ['255,255,255','226,236,255','206,222,255','255,244,230','255,232,206'];
    function rnd(seed){ return function(){ seed = (seed * 16807) % 2147483647; return (seed - 1) / 2147483646; }; }
    function build(){
      W = cv.clientWidth; H = cv.clientHeight; cv.width = W * dpr; cv.height = H * dpr; ctx.setTransform(dpr,0,0,dpr,0,0);
      var r = rnd(7919), n = Math.round(W * H / 900); stars = [];
      for (var i = 0; i < n; i++){
        var m = Math.pow(r(), 6);                 /* most stars faint, very few bright */
        var y = r() * H;
        var fade = Math.max(0, 1 - y / (H * 0.95)); /* fewer stars near the horizon glow */
        stars.push({ x: r() * W, y: y, size: 0.25 + m * 1.5, a: (0.18 + m * 0.82) * (0.35 + 0.65 * fade),
          c: tints[Math.floor(r() * (m > .3 ? tints.length : 3))], tw: m > .25 && r() < .5, ph: r() * 6.28, sp: .4 + r() * .8 });
      }
    }
    function draw(t){
      ctx.clearRect(0,0,W,H);
      for (var i = 0; i < stars.length; i++){
        var s = stars[i], a = s.a;
        if (s.tw && !reduce) a *= 0.82 + 0.18 * Math.sin(s.ph + (t || 0) / 1000 * s.sp);
        if (s.size > 1.45){
          var g = ctx.createRadialGradient(s.x, s.y, 0, s.x, s.y, s.size * 3.2);
          g.addColorStop(0, 'rgba(' + s.c + ',' + (a * .5) + ')'); g.addColorStop(1, 'rgba(' + s.c + ',0)');
          ctx.fillStyle = g; ctx.beginPath(); ctx.arc(s.x, s.y, s.size * 3.2, 0, 6.283); ctx.fill();
        }
        ctx.fillStyle = 'rgba(' + s.c + ',' + a + ')';
        ctx.beginPath(); ctx.arc(s.x, s.y, s.size, 0, 6.283); ctx.fill();
      }
      if (!reduce && vis) requestAnimationFrame(draw);
    }
    build(); draw(0);
    window.addEventListener('resize', function(){ build(); if (reduce) draw(0); });
    if (!reduce && 'IntersectionObserver' in window) new IntersectionObserver(function(en){ var was = vis; vis = en[0].isIntersecting; if (vis && !was) requestAnimationFrame(draw); }).observe(cv);
  });
})();
