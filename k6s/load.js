import http from "k6/http";
import { check, sleep, group } from "k6";
import { randomString } from "https://jslib.k6.io/k6-utils/1.2.0/index.js";

const BASE_URL = "https://gce.olympisai.com";

export const options = {
  scenarios: {
    dashboard_activity: {
      executor: "ramping-vus",
      startVUs: 1,
      stages: [
        { duration: "2m", target: 20 },
        { duration: "10m", target: 20 },
        { duration: "2m", target: 0 },
      ],
    },
  },
};

export default function() {
  group("Dashboard Reads", () => {
    let resHealth = http.get(`${BASE_URL}/healthcheck`);
    check(resHealth, { "Healthcheck 200": (r) => r.status === 200 });

    let resProfile = http.get(`${BASE_URL}/user/profile`);
    check(resProfile, { "Profile 200": (r) => r.status === 200 });

    let resList = http.get(`${BASE_URL}/stores/`);
    check(resList, { "List Stores 200": (r) => r.status === 200 });
  });

  sleep(Math.random() * 2 + 1);

  if (Math.random() < 0.05) {
    group("Schedule Job", () => {
      const payload = JSON.stringify({
        name: `store-${randomString(8)}`,
        url: `https://www.${randomString(5)}.com`,
      });

      const params = {
        headers: { "Content-Type": "application/json" },
      };

      let resPost = http.post(`${BASE_URL}/stores/`, payload, params);

      check(resPost, {
        "Job Created (200)": (r) => r.status === 200,
      });
    });
  }

  sleep(Math.random() * 2 + 1);
}
