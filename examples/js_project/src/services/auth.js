import { formatTitle } from '../utils/helpers.js';

let currentToken = null;

export function initAuth() {
  currentToken = 'demo-token-12345';
  console.log(formatTitle('Auth initialized'));
}

export function getToken() {
  return currentToken;
}

export function logout() {
  currentToken = null;
}
