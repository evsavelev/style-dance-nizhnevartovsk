'use strict';
const menuButton = document.querySelector('#mobile-menu-btn');
const menu = document.querySelector('#mobile-menu');
function closeMenu(returnFocus = false) {
  menu.hidden = true;
  menuButton.setAttribute('aria-expanded', 'false');
  menuButton.setAttribute('aria-label', 'Открыть меню');
  if (returnFocus) menuButton.focus();
}
menuButton.addEventListener('click', () => {
  const open = menu.hidden;
  menu.hidden = !open;
  menuButton.setAttribute('aria-expanded', String(open));
  menuButton.setAttribute('aria-label', open ? 'Закрыть меню' : 'Открыть меню');
});
menu.addEventListener('click', event => {
  if (event.target.closest('a')) closeMenu();
});
document.addEventListener('keydown', event => {
  if (event.key === 'Escape' && !menu.hidden) closeMenu(true);
});
document.addEventListener('click', event => {
  if (!menu.hidden && !event.target.closest('.site-header')) closeMenu();
});
matchMedia('(min-width:1200px)').addEventListener('change', event => {
  if (event.matches) closeMenu();
});
const filters = [...document.querySelectorAll('[data-filter]')];
const gallery = document.querySelector('#gallery-grid');
const pictures = [...gallery.querySelectorAll('.gallery-item')];
filters.forEach(button => button.addEventListener('click', () => {
  const selected = button.dataset.filter;
  filters.forEach(filter => filter.setAttribute('aria-pressed', String(filter === button)));
  pictures.forEach(picture => { picture.hidden = selected !== 'all' && picture.dataset.category !== selected; });
  gallery.classList.toggle('is-filtered', selected !== 'all');
  document.querySelector('#gallery-status').textContent = 'Показано изображений: ' + pictures.filter(picture => !picture.hidden).length;
}));
const dialog = document.querySelector('#photo-dialog');
const dialogImage = document.querySelector('#dialog-image');
let lastPicture;
pictures.forEach(picture => picture.addEventListener('click', event => {
  if (!dialog.showModal) return;
  event.preventDefault();
  lastPicture = picture;
  dialogImage.src = picture.getAttribute('href');
  dialogImage.alt = picture.querySelector('img').alt;
  document.querySelector('#dialog-caption').textContent = dialogImage.alt;
  dialog.showModal();
  document.documentElement.classList.add('dialog-open');
}));
dialog.querySelector('.dialog-close').addEventListener('click', () => dialog.close());
dialog.addEventListener('click', event => {
  if (event.target === dialog) {
    const bounds = dialog.getBoundingClientRect();
    if (event.clientX < bounds.left || event.clientX > bounds.right || event.clientY < bounds.top || event.clientY > bounds.bottom) dialog.close();
  }
});
dialog.addEventListener('close', () => {
  document.documentElement.classList.remove('dialog-open');
  lastPicture?.focus();
});
