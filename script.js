const toggle = document.querySelector('.menu-toggle');
const nav = document.querySelector('.site-nav');
const backdrop = document.getElementById('nav-backdrop');

function closeNavMenu() {
  if (!nav) return;
  nav.classList.remove('open');
  if (backdrop) backdrop.classList.remove('open');
  if (toggle) {
    toggle.classList.remove('open');
    toggle.setAttribute('aria-expanded', 'false');
    toggle.setAttribute('aria-label', 'Open navigation');
  }
  document.body.classList.remove('nav-locked');
  toggleLangDropdown(false);
}

if (toggle && nav) {
  toggle.addEventListener('click', (e) => {
    e.preventDefault();
    e.stopPropagation();
    const open = nav.classList.toggle('open');
    toggle.classList.toggle('open', open);
    if (backdrop) backdrop.classList.toggle('open', open);
    toggle.setAttribute('aria-expanded', String(open));
    toggle.setAttribute('aria-label', open ? 'Close navigation' : 'Open navigation');
    document.body.classList.toggle('nav-locked', open);
  });

  if (backdrop) {
    backdrop.addEventListener('click', (e) => {
      e.preventDefault();
      closeNavMenu();
    });
  }

  nav.querySelectorAll('a').forEach((link) => link.addEventListener('click', () => {
    closeNavMenu();
  }));

  window.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && nav.classList.contains('open')) {
      closeNavMenu();
    }
  });
}

const themeButton = document.querySelector('.theme-toggle');
const langSelect = document.getElementById('lang-select');
const langDropdown = document.getElementById('lang-dropdown');
const langDropdownBtn = document.getElementById('lang-dropdown-btn');
const langDropdownMenu = document.getElementById('lang-dropdown-menu');
const currentLangText = document.getElementById('current-lang-text');
const currentLangPill = document.getElementById('current-lang-pill');
const langOptions = document.querySelectorAll('.lang-option');

const LANG_CONFIG = {
  en: { label: 'English', code: 'EN' },
  ar: { label: 'العربية', code: 'AR' },
  es: { label: 'Español', code: 'ES' },
  fr: { label: 'Français', code: 'FR' },
  de: { label: 'Deutsch', code: 'DE' },
  ja: { label: '日本語', code: 'JA' },
  zh: { label: '中文', code: 'ZH' },
  it: { label: 'Italiano', code: 'IT' },
  ru: { label: 'Русский', code: 'RU' },
  hi: { label: 'हिन्दी', code: 'HI' },
  ko: { label: '한국어', code: 'KO' },
  tr: { label: 'Türkçe', code: 'TR' }
};

function toggleLangDropdown(show) {
  if (!langDropdown || !langDropdownBtn) return;
  const willOpen = typeof show === 'boolean' ? show : !langDropdown.classList.contains('open');
  langDropdown.classList.toggle('open', willOpen);
  langDropdownBtn.setAttribute('aria-expanded', String(willOpen));
}

if (langDropdownBtn) {
  langDropdownBtn.addEventListener('click', (e) => {
    e.preventDefault();
    e.stopPropagation();
    toggleLangDropdown();
  });
}

langOptions.forEach((btn) => {
  btn.addEventListener('click', (e) => {
    e.preventDefault();
    e.stopPropagation();
    const lang = btn.getAttribute('data-lang');
    if (lang) {
      applyLanguage(lang, true);
      toggleLangDropdown(false);
    }
  });
});

document.addEventListener('click', (e) => {
  if (langDropdown && langDropdown.classList.contains('open') && !langDropdown.contains(e.target)) {
    toggleLangDropdown(false);
  }
});

window.addEventListener('keydown', (e) => {
  if (e.key === 'Escape' && langDropdown && langDropdown.classList.contains('open')) {
    toggleLangDropdown(false);
    langDropdownBtn?.focus();
  }
});

function getActiveDictionary(lang) {
  const translations = window.PORTFOLIO_TRANSLATIONS || {};
  return translations[lang] || translations['en'] || {};
}

function setTheme(theme, persist = false) {
  document.documentElement.dataset.theme = theme;
  if (!themeButton) return;
  const currentLang = document.documentElement.lang || 'en';
  const dict = getActiveDictionary(currentLang);
  const target = theme === 'dark' ? 'light' : 'dark';
  themeButton.textContent = target === 'dark' ? (dict.nav_theme_dark || '◐ Dark mode') : (dict.nav_theme_light || '☼ Light mode');
  themeButton.setAttribute('aria-label', 'Switch to ' + target + ' mode');
  if (persist) localStorage.setItem('portfolio-theme', theme);
}

function applyLanguage(lang, persist = false) {
  const dict = getActiveDictionary(lang);
  document.documentElement.lang = lang;
  document.documentElement.dir = (lang === 'ar' ? 'rtl' : 'ltr');

  document.querySelectorAll('[data-i18n]').forEach((el) => {
    const key = el.getAttribute('data-i18n');
    const val = dict[key];
    if (val !== undefined) {
      if (val.includes('<') || val.includes('&')) {
        el.innerHTML = val;
      } else {
        el.textContent = val;
      }
    }
  });

  // Update custom dropdown trigger & options
  const info = LANG_CONFIG[lang] || { label: 'English', code: 'EN' };
  if (currentLangText) currentLangText.textContent = info.label;
  if (currentLangPill) currentLangPill.textContent = info.code;

  langOptions.forEach((btn) => {
    const isSelected = btn.getAttribute('data-lang') === lang;
    btn.classList.toggle('active', isSelected);
    btn.setAttribute('aria-selected', String(isSelected));
  });

  if (langSelect && langSelect.value !== lang) {
    langSelect.value = lang;
  }

  if (dict.meta_title) document.title = dict.meta_title;
  const metaDesc = document.querySelector('meta[name="description"]');
  if (metaDesc && dict.meta_desc) metaDesc.setAttribute('content', dict.meta_desc);

  // Sync theme button label
  const curTheme = document.documentElement.dataset.theme || 'light';
  setTheme(curTheme, false);

  // Update see-more buttons & contribution summaries
  document.querySelectorAll('.see-more').forEach((btn) => {
    btn.textContent = dict.see_more || 'See more';
  });
  document.querySelectorAll('.contribution summary').forEach((sum) => {
    sum.textContent = dict.my_contribution || 'My contribution';
  });

  // Update existing project dialogs
  document.querySelectorAll('.project-card').forEach((card, index) => {
    const dialog = document.getElementById(`project-details-${index + 1}`);
    if (!dialog) return;
    const info = card.querySelector('.project-info');
    const title = info?.querySelector('h3');
    const summary = info?.querySelector(':scope > p:not(.project-long)');
    const longDescription = info?.querySelector('.project-long');
    const contribution = info?.querySelector('.contribution p');

    const dialogTitle = dialog.querySelector('.dialog-heading h3');
    const dialogSummary = dialog.querySelector('.dialog-description p:first-child');
    const dialogLong = dialog.querySelector('.dialog-description p:nth-child(2)');
    const dialogContribHeading = dialog.querySelector('.dialog-contribution h4');
    const dialogContrib = dialog.querySelector('.dialog-contribution p');

    if (dialogTitle && title) dialogTitle.textContent = title.textContent;
    if (dialogSummary && summary) dialogSummary.textContent = summary.textContent;
    if (dialogLong && longDescription) dialogLong.textContent = longDescription.textContent;
    if (dialogContribHeading) dialogContribHeading.textContent = dict.my_contributions || 'My contributions';
    if (dialogContrib && contribution) dialogContrib.textContent = contribution.textContent;
  });

  if (persist) {
    localStorage.setItem('portfolio-lang', lang);
  }
  document.documentElement.dataset.i18nReady = 'true';
}

const currentTheme = document.documentElement.dataset.theme || 'light';
setTheme(currentTheme);
if (themeButton) {
  themeButton.addEventListener('click', () => {
    setTheme(document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark', true);
  });
}

if (langSelect) {
  langSelect.addEventListener('change', (e) => {
    applyLanguage(e.target.value, true);
  });
}

// Initial language application
const initialLang = window.__initialLang || localStorage.getItem('portfolio-lang') || 'en';
applyLanguage(initialLang, false);

const yearEl = document.querySelector('#year');
if (yearEl) yearEl.textContent = new Date().getFullYear();

const cards = document.querySelectorAll('.project-card, .timeline-item, .education-card');
if ('IntersectionObserver' in window && !matchMedia('(prefers-reduced-motion: reduce)').matches) {
  cards.forEach((card) => card.classList.add('js-reveal'));
  const observer = new IntersectionObserver((entries) => entries.forEach((entry) => {
    if (entry.isIntersecting) { entry.target.classList.add('is-visible'); observer.unobserve(entry.target); }
  }), { threshold: 0.08 });
  cards.forEach((card) => observer.observe(card));
}

// Turn each project card into a compact preview with a keyboard-accessible detail dialog.
document.querySelectorAll('.project-card').forEach((card, index) => {
  const info = card.querySelector('.project-info');
  const title = info?.querySelector('h3');
  const summary = info?.querySelector(':scope > p:not(.project-long)');
  const longDescription = info?.querySelector('.project-long');
  const contribution = info?.querySelector('.contribution p');
  if (!info || !title || !summary) return;

  const currentLang = document.documentElement.lang || 'en';
  const dict = getActiveDictionary(currentLang);

  const dialogId = `project-details-${index + 1}`;
  const more = document.createElement('button');
  more.className = 'see-more';
  more.type = 'button';
  more.textContent = dict.see_more || 'See more';
  more.setAttribute('aria-haspopup', 'dialog');
  more.setAttribute('aria-controls', dialogId);
  summary.after(more);

  const dialog = document.createElement('dialog');
  dialog.className = 'project-dialog';
  dialog.id = dialogId;
  dialog.setAttribute('aria-labelledby', `${dialogId}-title`);
  const heading = document.createElement('div');
  heading.className = 'dialog-heading';
  const dialogTitle = document.createElement('h3');
  dialogTitle.id = `${dialogId}-title`;
  dialogTitle.textContent = title.textContent;
  const close = document.createElement('button');
  close.className = 'dialog-close';
  close.type = 'button';
  close.setAttribute('aria-label', dict.dialog_close || 'Close project details');
  close.textContent = '×';
  heading.append(dialogTitle, close);
  const full = document.createElement('div');
  full.className = 'dialog-description';
  const summaryCopy = document.createElement('p');
  summaryCopy.textContent = summary.textContent;
  full.append(summaryCopy);
  if (longDescription) {
    const longCopy = document.createElement('p');
    longCopy.textContent = longDescription.textContent;
    full.append(longCopy);
  }
  dialog.append(heading, full);
  if (contribution) {
    const contributionSection = document.createElement('section');
    contributionSection.className = 'dialog-contribution';
    const contributionHeading = document.createElement('h4');
    contributionHeading.textContent = dict.my_contributions || 'My contributions';
    const contributionCopy = document.createElement('p');
    contributionCopy.textContent = contribution.textContent;
    contributionSection.append(contributionHeading, contributionCopy);
    dialog.append(contributionSection);
  }
  document.body.append(dialog);
  if (longDescription) longDescription.hidden = true;
  close.addEventListener('click', () => dialog.close());
  more.addEventListener('click', () => dialog.showModal());
  dialog.addEventListener('click', (event) => {
    if (event.target === dialog) dialog.close();
  });
  dialog.addEventListener('close', () => more.focus());
});

// Animate the contribution disclosure without changing its native keyboard behavior.
document.querySelectorAll('.contribution').forEach((disclosure) => {
  const body = disclosure.querySelector('p');
  if (!body) return;
  const wrapper = document.createElement('div');
  wrapper.className = 'contribution-body';
  body.before(wrapper);
  wrapper.append(body);
});
