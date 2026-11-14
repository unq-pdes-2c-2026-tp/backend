import { exerciseApi } from './common.js';

export const options = {
  stages: [
    { duration: '1m', target: 20 },
    { duration: '5m', target: 20 },
    { duration: '1m', target: 0 },
  ],
  thresholds: {
    http_req_duration: ['p(95)<1000', 'p(99)<2000'],
    http_req_failed: ['rate<0.01'],
    checks: ['rate>0.99'],
  },
};

export default function () {
  exerciseApi();
}
