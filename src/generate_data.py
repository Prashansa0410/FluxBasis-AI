import pandas as pd
import numpy as np
from faker import Faker

fake = Faker()

rows = []

for i in range(5000):

    flaky = np.random.choice([0, 1], p=[0.8, 0.2])

    duration = np.random.normal(20, 5)

    retry_count = np.random.randint(0, 5) if flaky else 0

    cpu_usage = np.random.randint(50, 95)

    network_latency = np.random.randint(100, 1000)

    failed_before = np.random.choice([0, 1], p=[0.7, 0.3])

    rows.append({
        "test_name": fake.word(),
        "duration": abs(duration),
        "retry_count": retry_count,
        "cpu_usage": cpu_usage,
        "network_latency": network_latency,
        "failed_before": failed_before,
        "flaky": flaky
    })

df = pd.DataFrame(rows)

df.to_csv("data/sample_test_results.csv", index=False)

print("Dataset generated successfully!")