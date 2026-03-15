import { Header } from './Header.jsx';
import { Footer } from './Footer.jsx';
import { fetchData } from '../services/api.js';

export function renderApp() {
  const header = Header();
  const footer = Footer();
  const data = fetchData('/api/home');

  return `<div>${header}${data}${footer}</div>`;
}

export function App() {
  return renderApp();
}
