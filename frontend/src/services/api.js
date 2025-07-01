import axios from 'axios';

const api = axios.create({
  baseURL: '/api/v1', // This will be proxied by Vite dev server
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export default api; 