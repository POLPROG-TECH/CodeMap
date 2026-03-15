import { formatTitle } from '../utils/helpers.js';

export function Footer() {
  const year = new Date().getFullYear();
  const title = formatTitle('Footer');
  return `<footer><p>${title} © ${year}</p></footer>`;
}
