
(function(){
  /* Same-origin endpoint: the server sends each enquiry to phmconsulting.advisory@gmail.com.
     No mailbox credentials ever live in this page. */
  var ENDPOINT = '/api/client-intake', TIMEOUT_MS = 20000;
  var form = document.getElementById('enquiry-form'), btn = document.getElementById('send-btn'), lbl = btn.querySelector('.lbl');
  var status = document.getElementById('form-status'), sum = document.getElementById('errsum');
  var amt = form.elements.budgetAmount, opts = [].slice.call(form.querySelectorAll('input[name="budgetOption"]'));
  var started = Date.now(), busy = false, done = false;

  /* Preselect the service chosen on the Services page */
  try { var pre = sessionStorage.getItem('phm-service'); if (pre){ form.querySelectorAll('input[name="service"]').forEach(function(r){ if (r.value === pre) r.checked = true; }); sessionStorage.removeItem('phm-service'); } } catch(e){}

  /* Budget: amount and the two alternatives are mutually exclusive.
     Choosing an alternative clears and dims the amount; typing an amount clears the alternative. */
  function dimAmount(on){ amt.classList.toggle('off', on); }
  opts.forEach(function(o){
    o.addEventListener('change', function(){
      if (o.checked){ opts.forEach(function(x){ if (x !== o) x.checked = false; }); amt.value = ''; dimAmount(true); }
      else if (!opts.some(function(x){ return x.checked; })) dimAmount(false);
      setErr('budget', '');
    });
  });
  amt.addEventListener('focus', function(){ dimAmount(false); });
  amt.addEventListener('input', function(){ if (amt.value){ opts.forEach(function(x){ x.checked = false; }); dimAmount(false); } setErr('budget', ''); });
  function setErr(key, msg){
    var p = document.getElementById(key + '-err'); if (p) p.textContent = msg;
    var el = key === 'service' ? form.querySelector('fieldset[aria-describedby="service-err"]') : key === 'budget' ? amt : form.elements[key];
    if (el && el.setAttribute){ if (msg) el.setAttribute('aria-invalid', 'true'); else el.removeAttribute('aria-invalid'); }
  }
  ['name','email'].forEach(function(k){ form.elements[k].addEventListener('input', function(){ setErr(k, ''); }); });
  form.querySelectorAll('input[name="service"]').forEach(function(r){ r.addEventListener('change', function(){ setErr('service', ''); }); });

  function validate(){
    var errs = [];
    var name = form.elements.name.value.trim(), email = form.elements.email.value.trim();
    var svc = form.querySelector('input[name="service"]:checked'), a = amt.value.trim();
    if (!name){ setErr('name', 'Enter your name.'); errs.push(['name', 'Enter your name.']); } else setErr('name', '');
    if (!email){ setErr('email', 'Enter your email address.'); errs.push(['email', 'Enter your email address.']); }
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email)){ setErr('email', 'Enter a valid email address, like name@example.com.'); errs.push(['email', 'Enter a valid email address.']); }
    else setErr('email', '');
    if (!svc){ setErr('service', 'Choose how we can help.'); errs.push(['service', 'Choose how we can help.']); } else setErr('service', '');
    if (a && !/^\$?\s?\d{1,3}(,?\d{3})*(\.\d{1,2})?$/.test(a)){ setErr('budget', 'Enter an amount in Canadian dollars, using numbers only.'); errs.push(['budgetAmount', 'Enter a budget amount using numbers only.']); } else setErr('budget', '');
    return errs;
  }

  function say(kind, msg, role){ status.className = 'status ' + kind; status.setAttribute('role', role || 'status'); status.textContent = msg; }

  form.addEventListener('submit', function(e){
    e.preventDefault();
    if (busy || done) return;
    var errs = validate();
    if (errs.length){
      sum.hidden = false;
      sum.innerHTML = '<p><b>Please fix ' + (errs.length === 1 ? 'this' : 'these ' + errs.length) + ' to continue:</b></p><ul>' + errs.map(function(x){ return '<li><a href="#' + (x[0] === 'service' ? 'service-err' : x[0]) + '">' + x[1] + '</a></li>'; }).join('') + '</ul>';
      sum.focus();
      return;
    }
    sum.hidden = true;
    var opt = opts.filter(function(x){ return x.checked; })[0];
    var data = {
      schemaVersion: '2.0', submittedAt: new Date().toISOString(), elapsedMs: Date.now() - started,
      name: form.elements.name.value.trim(), organization: form.elements.organization.value.trim(),
      email: form.elements.email.value.trim(), phone: form.elements.phone.value.trim(),
      service: form.querySelector('input[name="service"]:checked').value,
      challenge: form.elements.challenge.value.trim(),
      budgetAmount: amt.value.trim(), budgetOption: opt ? opt.value : '',
      websiteConfirm: form.elements.websiteConfirm.value
    };
    busy = true; btn.disabled = true; lbl.textContent = 'Sending…'; say('busy', 'Sending your enquiry…');
    var ctrl = ('AbortController' in window) ? new AbortController() : null;
    var timer = setTimeout(function(){ if (ctrl) ctrl.abort(); }, TIMEOUT_MS);
    fetch(ENDPOINT, { method: 'POST', credentials: 'same-origin', headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' }, body: JSON.stringify(data), signal: ctrl ? ctrl.signal : undefined })
      .then(function(res){ return res.json().catch(function(){ return null; }).then(function(j){ if (res.ok && j && j.ok === true) return true; throw new Error('not accepted'); }); })
      .then(function(){
        done = true; busy = false; form.reset(); dimAmount(false); lbl.textContent = 'Sent';
        say('ok', 'Thanks for reaching out! We’ve received your enquiry and will be in touch soon.');
        window.phmTrack && window.phmTrack('generate_lead');
      })
      .catch(function(){
        busy = false; btn.disabled = false; lbl.textContent = 'Let’s Connect';
        say('err', 'Sorry, we couldn’t send your enquiry. Your answers are still here. Please try again, or email us at phmconsulting.advisory@gmail.com.', 'alert');
      })
      .then(function(){ clearTimeout(timer); });
  });
})();
