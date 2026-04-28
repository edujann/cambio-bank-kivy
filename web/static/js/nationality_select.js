/**
 * Searchable nationality select — allowed countries only (PROHIBITED_COUNTRIES excluded).
 * Usage: initNationalitySelect(wrapperId, hiddenInputId, currentValue)
 *   wrapperId     — id of a <div> that will receive the component
 *   hiddenInputId — id of the hidden <input> that stores the value (used by existing form code)
 *   currentValue  — pre-fill value (nationality string already stored)
 */

const NATIONALITIES = [
  {v:'Afghan',l:'Afghan'},
  {v:'Albanian',l:'Albanian'},
  {v:'Algerian',l:'Algerian'},
  {v:'American',l:'American'},
  {v:'Angolan',l:'Angolan'},
  {v:'Argentine',l:'Argentine'},
  {v:'Armenian',l:'Armenian'},
  {v:'Australian',l:'Australian'},
  {v:'Austrian',l:'Austrian'},
  {v:'Azerbaijani',l:'Azerbaijani'},
  {v:'Bangladeshi',l:'Bangladeshi'},
  {v:'Belgian',l:'Belgian'},
  {v:'Bolivian',l:'Bolivian'},
  {v:'Brazilian',l:'Brazilian'},
  {v:'British',l:'British'},
  {v:'Bulgarian',l:'Bulgarian'},
  {v:'Burkinabe',l:'Burkinabe'},
  {v:'Cameroonian',l:'Cameroonian'},
  {v:'Canadian',l:'Canadian'},
  {v:'Chilean',l:'Chilean'},
  {v:'Chinese',l:'Chinese'},
  {v:'Colombian',l:'Colombian'},
  {v:'Congolese',l:'Congolese (Rep. of Congo)'},
  {v:'Costa Rican',l:'Costa Rican'},
  {v:'Croatian',l:'Croatian'},
  {v:'Czech',l:'Czech'},
  {v:'Danish',l:'Danish'},
  {v:'Dominican',l:'Dominican'},
  {v:'Dutch',l:'Dutch'},
  {v:'Ecuadorian',l:'Ecuadorian'},
  {v:'Egyptian',l:'Egyptian'},
  {v:'Eritrean',l:'Eritrean'},
  {v:'Ethiopian',l:'Ethiopian'},
  {v:'Finnish',l:'Finnish'},
  {v:'French',l:'French'},
  {v:'Georgian',l:'Georgian'},
  {v:'German',l:'German'},
  {v:'Ghanaian',l:'Ghanaian'},
  {v:'Greek',l:'Greek'},
  {v:'Guatemalan',l:'Guatemalan'},
  {v:'Honduran',l:'Honduran'},
  {v:'Hungarian',l:'Hungarian'},
  {v:'Indian',l:'Indian'},
  {v:'Indonesian',l:'Indonesian'},
  {v:'Iraqi',l:'Iraqi'},
  {v:'Irish',l:'Irish'},
  {v:'Italian',l:'Italian'},
  {v:'Ivorian',l:'Ivorian (Côte d\'Ivoire)'},
  {v:'Jamaican',l:'Jamaican'},
  {v:'Japanese',l:'Japanese'},
  {v:'Jordanian',l:'Jordanian'},
  {v:'Kenyan',l:'Kenyan'},
  {v:'Kuwaiti',l:'Kuwaiti'},
  {v:'Laotian',l:'Laotian'},
  {v:'Malaysian',l:'Malaysian'},
  {v:'Mexican',l:'Mexican'},
  {v:'Moldovan',l:'Moldovan'},
  {v:'Monégasque',l:'Monégasque'},
  {v:'Moroccan',l:'Moroccan'},
  {v:'Mozambican',l:'Mozambican'},
  {v:'Namibian',l:'Namibian'},
  {v:'Nepalese',l:'Nepalese'},
  {v:'New Zealander',l:'New Zealander'},
  {v:'Nigerian',l:'Nigerian'},
  {v:'Norwegian',l:'Norwegian'},
  {v:'Pakistani',l:'Pakistani'},
  {v:'Panamanian',l:'Panamanian'},
  {v:'Paraguayan',l:'Paraguayan'},
  {v:'Peruvian',l:'Peruvian'},
  {v:'Philippine',l:'Philippine'},
  {v:'Polish',l:'Polish'},
  {v:'Portuguese',l:'Portuguese'},
  {v:'Qatari',l:'Qatari'},
  {v:'Romanian',l:'Romanian'},
  {v:'Saudi',l:'Saudi'},
  {v:'Senegalese',l:'Senegalese'},
  {v:'Serbian',l:'Serbian'},
  {v:'Singaporean',l:'Singaporean'},
  {v:'South African',l:'South African'},
  {v:'South Korean',l:'South Korean'},
  {v:'Spanish',l:'Spanish'},
  {v:'Sri Lankan',l:'Sri Lankan'},
  {v:'Sudanese',l:'Sudanese'},
  {v:'Swedish',l:'Swedish'},
  {v:'Swiss',l:'Swiss'},
  {v:'Syrian',l:'Syrian'},
  {v:'Taiwanese',l:'Taiwanese'},
  {v:'Tanzanian',l:'Tanzanian'},
  {v:'Thai',l:'Thai'},
  {v:'Togolese',l:'Togolese'},
  {v:'Tunisian',l:'Tunisian'},
  {v:'Turkish',l:'Turkish'},
  {v:'Ugandan',l:'Ugandan'},
  {v:'Ukrainian',l:'Ukrainian'},
  {v:'Uruguayan',l:'Uruguayan'},
  {v:'Vietnamese',l:'Vietnamese'},
  {v:'Zambian',l:'Zambian'},
];

const NAT_SELECT_CSS = `
.nat-wrap { position:relative; }
.nat-search { width:100%; box-sizing:border-box; cursor:pointer; }
.nat-dropdown {
  display:none; position:absolute; z-index:9999; left:0; right:0; top:100%;
  background:var(--cor-card, #fff); border:1px solid var(--cor-borda, #ccc);
  border-radius:0 0 6px 6px; max-height:220px; overflow-y:auto;
  box-shadow:0 4px 12px rgba(0,0,0,.15);
}
.nat-dropdown.open { display:block; }
.nat-option {
  padding:7px 10px; cursor:pointer; font-size:13px;
  color:var(--cor-texto, #333);
}
.nat-option:hover, .nat-option.highlighted { background:var(--cor-hover, rgba(0,120,212,.1)); }
.nat-option.selected { font-weight:600; color:var(--cor-primaria, #0078d4); }
`;

(function injectNatCss() {
  if (document.getElementById('nat-select-style')) return;
  const s = document.createElement('style');
  s.id = 'nat-select-style';
  s.textContent = NAT_SELECT_CSS;
  document.head.appendChild(s);
})();

/**
 * @param {string} wrapperId    - id of container div
 * @param {string} hiddenId     - id of the hidden input (existing code reads this)
 * @param {string} [current]    - current nationality value
 * @param {object} [opts]
 * @param {string} [opts.placeholder]
 * @param {string} [opts.inputClass]  - CSS class(es) for the visible input (e.g. "form-control")
 * @param {string} [opts.inputStyle]  - inline style string for the visible input
 */
function initNationalitySelect(wrapperId, hiddenId, current, opts) {
  opts = opts || {};
  const wrap = document.getElementById(wrapperId);
  if (!wrap) return;

  wrap.classList.add('nat-wrap');
  wrap.innerHTML = '';

  const searchInput = document.createElement('input');
  searchInput.type = 'text';
  searchInput.className = 'nat-search ' + (opts.inputClass || '');
  searchInput.placeholder = opts.placeholder || 'Type to search nationality…';
  searchInput.autocomplete = 'off';
  searchInput.setAttribute('readonly', 'readonly');
  if (opts.inputStyle) searchInput.style.cssText = opts.inputStyle;

  const hiddenInput = document.createElement('input');
  hiddenInput.type = 'hidden';
  hiddenInput.id = hiddenId;

  const dropdown = document.createElement('div');
  dropdown.className = 'nat-dropdown';

  wrap.appendChild(searchInput);
  wrap.appendChild(hiddenInput);
  wrap.appendChild(dropdown);

  function renderOptions(filter) {
    const q = (filter || '').toLowerCase();
    dropdown.innerHTML = '';
    const filtered = q ? NATIONALITIES.filter(n => n.l.toLowerCase().includes(q)) : NATIONALITIES;
    if (!filtered.length) {
      dropdown.innerHTML = '<div class="nat-option" style="color:#aaa;font-style:italic;">No results</div>';
      return;
    }
    filtered.forEach(n => {
      const opt = document.createElement('div');
      opt.className = 'nat-option' + (hiddenInput.value === n.v ? ' selected' : '');
      opt.textContent = n.l;
      opt.addEventListener('mousedown', e => {
        e.preventDefault();
        hiddenInput.value = n.v;
        searchInput.value = n.l;
        searchInput.removeAttribute('readonly');
        searchInput.setAttribute('readonly', 'readonly');
        dropdown.classList.remove('open');
        hiddenInput.dispatchEvent(new Event('change', {bubbles:true}));
      });
      dropdown.appendChild(opt);
    });
  }

  searchInput.addEventListener('click', () => {
    searchInput.removeAttribute('readonly');
    renderOptions('');
    dropdown.classList.add('open');
  });

  searchInput.addEventListener('input', () => {
    renderOptions(searchInput.value);
    dropdown.classList.add('open');
  });

  searchInput.addEventListener('blur', () => {
    setTimeout(() => dropdown.classList.remove('open'), 150);
    // if typed text doesn't match any option, restore last valid value
    const match = NATIONALITIES.find(n => n.l.toLowerCase() === searchInput.value.toLowerCase());
    if (match) {
      hiddenInput.value = match.v;
      searchInput.value = match.l;
    } else if (hiddenInput.value) {
      const prev = NATIONALITIES.find(n => n.v === hiddenInput.value);
      if (prev) searchInput.value = prev.l;
    } else {
      searchInput.value = '';
    }
  });

  // pre-fill
  if (current) {
    const found = NATIONALITIES.find(n => n.v === current || n.l.toLowerCase() === (current||'').toLowerCase());
    if (found) {
      hiddenInput.value = found.v;
      searchInput.value = found.l;
    } else {
      hiddenInput.value = current;
      searchInput.value = current;
    }
  }
}
