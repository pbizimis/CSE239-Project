import http from "k6/http";
import { check, sleep, group } from "k6";
import { randomString } from "https://jslib.k6.io/k6-utils/1.2.0/index.js";

const BASE_URL = "https://gce.olympisai.com";

export const options = {
  scenarios: {
    job_scheduling_stress: {
      executor: "ramping-vus",
      startVUs: 10,
      stages: [
        // Start at 10 VUs and ramp to 100 over 20 minutes.
        { duration: "20m", target: 100 },
      ],
    },
  },
};

export default function() {
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

  sleep(Math.random() * 2 + 1);
}
