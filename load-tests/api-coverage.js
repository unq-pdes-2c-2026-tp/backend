import { exerciseAllReadEndpoints, setup } from './common.js';

export const options = {
  scenarios: {
    api_coverage: {
      executor: 'per-vu-iterations',
      vus: Number(__ENV.READ_VUS || 1),
      iterations: Number(__ENV.READ_ITERATIONS || 1),
      maxDuration: '10m',
    },
  },
  thresholds: {
    http_req_failed: ['rate<0.01'],
    checks: ['rate>0.99'],
  },
};

export { setup };

export default function (data) {
  exerciseAllReadEndpoints(data);
}
