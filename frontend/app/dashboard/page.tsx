'use client';

import { useEffect, useState } from 'react';
import {
  LineChart,
  Line,
  ResponsiveContainer,
  Tooltip,
  BarChart,
  Bar,
  XAxis,
  YAxis,
} from 'recharts';
import { Shell, Stat, Empty } from '@/components/shell';
import { Analytics, getJson } from '@/lib/api';

export default function Dashboard() {
  const [data, setData] = useState<Analytics | null>(null);
  const [err, setErr] = useState('');

  useEffect(() => {
    getJson<Analytics>('/api/v1/analytics')
      .then(setData)
      .catch((e) => setErr(e.message));
  }, []);

  return (
    <Shell>
      <h1 className="text-4xl font-semibold tracking-tight">
        CI reliability overview
      </h1>
      <p className="mt-3 muted">
        What is happening with your CI reliability?
      </p>

      {err && <Empty title={`Backend unavailable: ${err}`} />}

      {!data && !err && (
        <div className="mt-8 grid gap-4 md:grid-cols-4">
          {[1, 2, 3, 4].map((i) => (
            <div className="card h-32 animate-pulse" key={i} />
          ))}
        </div>
      )}

      {data && (
        <>
          <div className="mt-8 grid gap-4 md:grid-cols-5">
            <Stat
              label="Reliability Score"
              value={`${data.reliability_score}%`}
            />
            <Stat label="Tests analyzed" value={data.tests_analyzed} />
            <Stat label="Flaky tests" value={data.flaky_tests} />
            <Stat label="At-risk tests" value={data.at_risk_tests} />
            <Stat
              label="Model accuracy"
              value={data.model_accuracy ? `${data.model_accuracy}%` : 'N/A'}
            />
          </div>

          <div className="mt-8 grid gap-6 lg:grid-cols-2">
            <div className="card p-6">
              <h2 className="font-medium">Reliability trend</h2>
              <ResponsiveContainer height={260}>
                <LineChart data={data.reliability_trend}>
                  <Tooltip />
                  <Line
                    type="monotone"
                    dataKey="score"
                    stroke="#2563eb"
                    strokeWidth={2}
                    dot={false}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>

            <div className="card p-6">
              <h2 className="font-medium">Flaky-test trend</h2>
              <ResponsiveContainer height={260}>
                <BarChart data={data.flaky_trend}>
                  <XAxis dataKey="date" hide />
                  <YAxis />
                  <Tooltip />
                  <Bar
                    dataKey="flaky"
                    fill="#111827"
                    radius={[8, 8, 0, 0]}
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="mt-8 grid gap-6 lg:grid-cols-2">
            <div className="card p-6">
              <h2 className="font-medium">Top flaky tests</h2>
              {data.top_flaky_tests.length ? (
                data.top_flaky_tests.map((t) => (
                  <p
                    className="mt-4 flex justify-between border-b pb-3 text-sm"
                    key={t.id}
                  >
                    <span>{t.test_name}</span>
                    <b>{Math.round(t.flaky_probability * 100)}%</b>
                  </p>
                ))
              ) : (
                <Empty title="No flaky tests in the available dataset." />
              )}
            </div>

            <div className="card p-6">
              <h2 className="font-medium">Recent runs</h2>
              {data.recent_runs.map((r) => (
                <p
                  className="mt-4 flex justify-between border-b pb-3 text-sm"
                  key={r.id}
                >
                  <span>{r.id}</span>
                  <span>{r.reliability_score}% reliable</span>
                </p>
              ))}
            </div>
          </div>
        </>
      )}
    </Shell>
  );
}
