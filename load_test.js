import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '10s', target: 20 },  // Ramp-up to 20 users
    { duration: '30s', target: 50 },  // High load to test HPA & stability
    { duration: '10s', target: 0 },   // Ramp-down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'], // 95% of requests must complete within 500ms
    http_req_failed: ['rate<0.01'],    // Error rate must be less than 1%
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://127.0.0.1:8000';

export default function () {
  // Test Health endpoint
  let healthRes = http.get(`${BASE_URL}/health`);
  check(healthRes, {
    'health status is 200': (r) => r.status === 200,
    'health response ok': (r) => r.json('status') === 'ok',
  });

  // Test Scheduler student retrieval endpoint
  let studentRes = http.get(`${BASE_URL}/api/v1/scheduler/student/test-student`);
  check(studentRes, {
    'student schedules status is 200': (r) => r.status === 200,
  });

  // Test Metrics endpoint
  let metricsRes = http.get(`${BASE_URL}/metrics`);
  check(metricsRes, {
    'metrics status is 200': (r) => r.status === 200,
  });

  sleep(0.5);
}
