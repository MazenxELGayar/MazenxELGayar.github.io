const toggle = document.querySelector('.menu-toggle');
const nav = document.querySelector('.site-nav');
if (toggle && nav) {
  toggle.addEventListener('click', () => {
    const open = nav.classList.toggle('open');
    toggle.setAttribute('aria-expanded', String(open));
    toggle.setAttribute('aria-label', open ? 'Close navigation' : 'Open navigation');
  });
  nav.querySelectorAll('a').forEach((link) => link.addEventListener('click', () => {
    nav.classList.remove('open');
    toggle.setAttribute('aria-expanded', 'false');
    toggle.setAttribute('aria-label', 'Open navigation');
  }));
}
const themeButton = document.querySelector('.theme-toggle');
const savedTheme = localStorage.getItem('portfolio-theme');
const initialTheme = savedTheme === 'light' || savedTheme === 'dark'
  ? savedTheme
  : (matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
function setTheme(theme, persist = false) {
  document.documentElement.dataset.theme = theme;
  if (!themeButton) return;
  const target = theme === 'dark' ? 'light' : 'dark';
  themeButton.textContent = (target === 'dark' ? '◐ Dark mode' : '☼ Light mode');
  themeButton.setAttribute('aria-label', 'Switch to ' + target + ' mode');
  if (persist) localStorage.setItem('portfolio-theme', theme);
}
setTheme(initialTheme);
if (themeButton) themeButton.addEventListener('click', () => {
  setTheme(document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark', true);
});
document.querySelector('#year').textContent = new Date().getFullYear();
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

  const dialogId = `project-details-${index + 1}`;
  const more = document.createElement('button');
  more.className = 'see-more';
  more.type = 'button';
  more.textContent = 'See more';
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
  close.setAttribute('aria-label', 'Close project details');
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
    contributionHeading.textContent = 'My contributions';
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
