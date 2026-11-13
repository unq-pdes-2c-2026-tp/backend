import http from 'k6/http';
import { check, sleep } from 'k6';

const baseUrl = (__ENV.BASE_URL || 'http://localhost:8000').replace(/\/+$/, '');
const endpoints = (__ENV.ENDPOINTS || '/api/hotels/,/api/agencies/')
  .split(',')
  .map((endpoint) => endpoint.trim())
  .filter(Boolean);

if (endpoints.length === 0 || endpoints.some((endpoint) => !endpoint.startsWith('/'))) {
  throw new Error('Los endpoints deben contener rutas separadas por comas que comiencen con /.');
}

export function exerciseApi() {
  const endpoint = endpoints[(__VU + __ITER) % endpoints.length];
  const response = http.get(`${baseUrl}${endpoint}`, {
    tags: { endpoint },
  });

  check(response, {
    [`${endpoint} returns a successful response`]: (result) =>
      result.status >= 200 && result.status < 300,
  });

  sleep(Number(__ENV.THINK_TIME || 1));
}
