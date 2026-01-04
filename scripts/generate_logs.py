import random, time, requests
from datetime import datetime

URL = "http://localhost:8080/api/logs"
SERVICES = ["auth", "payments", "orders", "inventory"]
LEVELS = ["INFO", "WARN", "ERROR"]

def main():
    for i in range(50):
        level = random.choices(LEVELS, weights=[70, 20, 10])[0]
        payload = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level,
            "service": random.choice(SERVICES),
            "message": f"event={i} level={level} something happened"
        }
        r = requests.post(URL, json=payload, timeout=5)
        print(r.status_code, r.json())
        time.sleep(0.05)

if __name__ == "__main__":
    main()
