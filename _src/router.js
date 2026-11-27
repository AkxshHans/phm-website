
(function(){
  var pages = [].slice.call(document.querySelectorAll('.page'));
  var titles = %s;
  function show(hash){
    var id = (hash || '').replace('#','') || 'home';
    var target = document.getElementById(id);
    var page = target && target.closest ? target.closest('.page') : null;
    if (!page){ page = document.getElementById('home'); target = page; }
    var changed = page.hidden;
    pages.forEach(function(p){ p.hidden = p !== page; });
    document.body.setAttribute('data-page', page.id);
    document.title = titles[page.id] + ' · Preview';
    var navId = page.id === 'canadian-market-entry' ? 'services' : page.id;
    document.querySelectorAll('.nav a').forEach(function(a){ if (a.getAttribute('href') === '#' + navId) a.setAttribute('aria-current','page'); else a.removeAttribute('aria-current'); });
    if (page.id === 'contact'){ try { var pre = sessionStorage.getItem('phm-service'); if (pre){ document.querySelectorAll('input[name="service"]').forEach(function(r){ r.checked = r.value === pre; }); sessionStorage.removeItem('phm-service'); } } catch(e){} }
    window.dispatchEvent(new Event('resize'));
    requestAnimationFrame(function(){
      var hdr = document.querySelector('.hdr'), off = (hdr ? hdr.offsetHeight : 90) + 16;
      var y = target === page ? 0 : target.getBoundingClientRect().top + window.scrollY - off;
      if (window.__lenis) window.__lenis.scrollTo(y, { immediate: changed }); else window.scrollTo({ top: y, behavior: changed ? 'auto' : 'smooth' });
      window.dispatchEvent(new Event('scroll'));
    });
  }
  window.addEventListener('hashchange', function(){ show(location.hash); });
  show(location.hash);
})();
