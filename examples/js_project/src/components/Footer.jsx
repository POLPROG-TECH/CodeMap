import { formatTitle } from '../utils/helpers.js';

export function Header() {
  const title = formatTitle('My Application');
  return `<header><h1>${title}</h1></header>`;
}
