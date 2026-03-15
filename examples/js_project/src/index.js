import { renderApp } from './components/App.jsx';
import { initAuth } from './services/auth.js';

initAuth();
renderApp();

console.log('Application started');
