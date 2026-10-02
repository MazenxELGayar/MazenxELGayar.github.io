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
