import http from 'k6/http';
import { check, sleep } from 'k6';

export const baseUrl = (__ENV.BASE_URL || 'http://localhost:4000').replace(/\/+$/, '');

const adminEmail = __ENV.LOAD_TEST_ADMIN_EMAIL || 'admin@gmail.com';
const adminPassword = __ENV.LOAD_TEST_ADMIN_PASSWORD || 'admin';
const userEmail = __ENV.LOAD_TEST_USER_EMAIL || 'user@gmail.com';
const userPassword = __ENV.LOAD_TEST_USER_PASSWORD || 'user';
const thinkTime = Number(__ENV.THINK_TIME || 1);

function headers(token) {
  return { Authorization: `Token ${token}` };
}

function login(email, password) {
  const response = http.post(
    `${baseUrl}/api/login/`,
    JSON.stringify({ email, password }),
    { headers: { 'Content-Type': 'application/json' }, tags: { endpoint: '/api/login/' } },
  );
  const token = response.headers.Authorization || response.headers.authorization;

  if (response.status !== 200 || !token) {
    throw new Error(`Load-test login failed with status ${response.status}.`);
  }

  return token;
}

function getCollection(path, token) {
  const response = http.get(`${baseUrl}${path}`, {
    headers: headers(token),
    tags: { endpoint: path },
  });

  if (response.status !== 200) {
    throw new Error(`Could not load ${path}: HTTP ${response.status}.`);
  }

  const body = response.json();
  return Array.isArray(body) ? body : body.results || [];
}

function firstId(items, environmentVariable) {
  return __ENV[environmentVariable] || (items.length ? items[0].id : null);
}

export function setup() {
  const adminToken = login(adminEmail, adminPassword);
  const userToken = login(userEmail, userPassword);

  const agencies = getCollection('/api/agencies/', adminToken);
  const hotels = getCollection('/api/hotels/', adminToken);
  const packages = getCollection('/api/packages/', adminToken);
  const purchases = getCollection('/api/purchases/', adminToken);
  const favorites = getCollection('/api/favorites/', userToken);
  const reviews = getCollection('/api/reviews/', adminToken);
  const users = getCollection('/api/users/', adminToken);

  const agencyId = firstId(agencies, 'LOAD_TEST_AGENCY_ID');
  const hotelId = firstId(hotels, 'LOAD_TEST_HOTEL_ID');
  const packageId = firstId(packages, 'LOAD_TEST_PACKAGE_ID');
  const purchaseId = firstId(purchases, 'LOAD_TEST_PURCHASE_ID');
  const favoriteId = firstId(favorites, 'LOAD_TEST_FAVORITE_ID');
  const reviewId = firstId(reviews, 'LOAD_TEST_REVIEW_ID');
  const userId = firstId(users, 'LOAD_TEST_USER_ID');

  const endpoints = [
    { path: '/api/agencies/', token: adminToken },
    { path: '/api/agencies/?search=travel', token: adminToken },
    { path: '/api/agencies/detailed/', token: adminToken },
    { path: '/api/hotels/', token: adminToken },
    { path: '/api/hotels/?search=hotel', token: adminToken },
    { path: '/api/packages/', token: adminToken },
    { path: '/api/packages/?search=travel', token: adminToken },
    { path: '/api/flights/', token: adminToken },
    { path: '/api/flights/?search=Buenos%20Aires', token: adminToken },
    { path: '/api/purchases/', token: adminToken },
    { path: '/api/purchases/top-spenders/', token: adminToken },
    { path: '/api/purchases/top-cities-by-purchases/', token: adminToken },
    { path: '/api/purchases/top-cities-by-reviews/', token: adminToken },
    { path: '/api/purchases/top-agencies-by-revenue/', token: adminToken },
    { path: '/api/favorites/', token: userToken },
    { path: '/api/reviews/', token: adminToken },
    { path: '/api/users/', token: adminToken },
    { path: '/api/schema/', token: adminToken },
    { path: '/api/schema/swagger-ui/', token: adminToken },
  ];

  if (agencyId) {
    endpoints.push({ path: `/api/agencies/${agencyId}/`, token: adminToken });
    endpoints.push({ path: `/api/packages/?agency_id=${agencyId}`, token: adminToken });
  }
  if (hotelId) {
    endpoints.push({ path: `/api/hotels/${hotelId}/`, token: adminToken });
  }
  if (packageId) {
    endpoints.push({ path: `/api/packages/${packageId}/`, token: adminToken });
    endpoints.push({ path: `/api/favorites/?package=${packageId}`, token: userToken });
    endpoints.push({ path: `/api/reviews/?package=${packageId}`, token: adminToken });
  }
  if (purchaseId) {
    endpoints.push({ path: `/api/purchases/${purchaseId}/`, token: adminToken });
    endpoints.push({
      path: `/api/reviews/?package_purchase=${purchaseId}`,
      token: adminToken,
    });
  }
  if (favoriteId) {
    endpoints.push({ path: `/api/favorites/${favoriteId}/`, token: userToken });
  }
  if (reviewId) {
    endpoints.push({ path: `/api/reviews/${reviewId}/`, token: adminToken });
  }
  if (userId) {
    endpoints.push({ path: `/api/users/${userId}/`, token: adminToken });
  }

  return { endpoints };
}

export function exerciseApi(data) {
  const endpoint = data.endpoints[(__VU + __ITER) % data.endpoints.length];
  const response = http.get(`${baseUrl}${endpoint.path}`, {
    headers: headers(endpoint.token),
    tags: { endpoint: endpoint.path },
  });

  check(response, {
    [`GET ${endpoint.path} returns a successful response`]: (result) =>
      result.status >= 200 && result.status < 300,
  });
  sleep(thinkTime);
}

export function exerciseAllReadEndpoints(data) {
  for (const endpoint of data.endpoints) {
    const response = http.get(`${baseUrl}${endpoint.path}`, {
      headers: headers(endpoint.token),
      tags: { endpoint: endpoint.path },
    });

    check(response, {
      [`GET ${endpoint.path} returns a successful response`]: (result) =>
        result.status >= 200 && result.status < 300,
    });
  }
  sleep(thinkTime);
}
