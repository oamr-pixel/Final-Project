// === Cloud Generation ===
function createClouds() {
  const container = document.getElementById('clouds');
  if (!container) return;

  const count = 8;
  const fragment = document.createDocumentFragment();

  for (let i = 0; i < count; i += 1) {
    const cloud = document.createElement('div');
    const size = 80 + Math.random() * 120;

    cloud.className = 'cloud';
    cloud.style.width = `${size}px`;
    cloud.style.height = `${size * 0.4}px`;
    cloud.style.top = `${Math.random() * 70}%`;
    cloud.style.left = '-220px';
    cloud.style.animationDuration = `${40 + Math.random() * 60}s`;
    cloud.style.animationDelay = `${-Math.random() * 80}s`;
    cloud.style.opacity = 0.4 + Math.random() * 0.3;

    fragment.appendChild(cloud);
  }

  container.appendChild(fragment);
}

// === Sparkle Stars ===
function createStars() {
  const container = document.getElementById('stars');
  if (!container) return;

  const count = 20;
  const fragment = document.createDocumentFragment();

  for (let i = 0; i < count; i += 1) {
    const star = document.createElement('div');
    const size = 2 + Math.random() * 3;

    star.className = 'star';
    star.style.left = `${Math.random() * 100}%`;
    star.style.top = `${Math.random() * 100}%`;
    star.style.animationDelay = `${Math.random() * 3}s`;
    star.style.width = `${size}px`;
    star.style.height = `${size}px`;

    fragment.appendChild(star);
  }

  container.appendChild(fragment);
}

// === Scroll Reveal ===
function setupScrollReveal() {
  const sections = document.querySelectorAll('.section');
  if (!sections.length) return;

  if (!('IntersectionObserver' in window)) {
    sections.forEach((section) => section.classList.add('visible'));
    return;
  }

  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12 });

  sections.forEach((section) => observer.observe(section));
}

// === Skill Tag Hover Colors ===
function setupSkillColors() {
  const colors = ['#ffd6e0', '#e8d5f5', '#c8e6ff', '#c8f7dc', '#ffe5cc', '#fff5cc'];

  document.querySelectorAll('.skill-tag').forEach((tag, index) => {
    tag.addEventListener('mouseenter', () => {
      tag.style.background = colors[index % colors.length];
    });

    tag.addEventListener('mouseleave', () => {
      tag.style.background = '';
    });
  });
}

// === Active Tab State ===
function setupActiveTabs() {
  const tabs = document.querySelectorAll('.tab[href^="#"]');
  const sections = [...tabs]
    .map((tab) => document.querySelector(tab.getAttribute('href')))
    .filter(Boolean);

  if (!tabs.length || !sections.length || !('IntersectionObserver' in window)) return;

  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return;

      tabs.forEach((tab) => {
        tab.classList.toggle('active', tab.getAttribute('href') === `#${entry.target.id}`);
      });
    });
  }, {
    rootMargin: '-42% 0px -50% 0px',
    threshold: 0,
  });

  sections.forEach((section) => observer.observe(section));
}

// === Optional Avatar Fallback ===
function setupAvatarFallback() {
  const avatar = document.getElementById('avatarImage');
  if (!avatar) return;

  avatar.addEventListener('error', () => {
    avatar.classList.add('is-missing');
  });
}

// === Init ===
document.addEventListener('DOMContentLoaded', () => {
  createClouds();
  createStars();
  setupScrollReveal();
  setupSkillColors();
  setupActiveTabs();
  setupAvatarFallback();
});
