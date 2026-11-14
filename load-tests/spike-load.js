import { exerciseApi } from './common.js';

export const options = {
  stages: [
    { duration: '30s', target: 5 },
    { duration: '10s', target: 50 },
    { duration: '1m', target: 50 },
    { duration: '10s', target: 5 },
    { duration: '30s', target: 0 },
  ],
  thresholds: {
    http_req_duration: ['p(95)<1500', 'p(99)<3000'],
    http_req_failed: ['rate<0.01'],
    checks: ['rate>0.99'],
  },
};

export default function () {
  exerciseApi();
}
