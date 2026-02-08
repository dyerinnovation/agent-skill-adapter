import { useApi } from "../hooks/useApi";
import { getDashboardStats } from "../api/client";

export default function Dashboard() {
  const { data: stats, loading, error } = useApi(getDashboardStats);

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-6">Dashboard</h1>
      {loading && <p className="text-gray-500">Loading...</p>}
      {error && <p className="text-red-600">Error: {error}</p>}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card title="Total Skills" value={stats.total_skills} />
          <Card title="Active Training Jobs" value={stats.active_training_jobs} />
          <Card title="Recent Avg Eval Score" value={`${(stats.recent_eval_avg_score * 100).toFixed(1)}%`} />
        </div>
      )}
    </div>
  );
}

function Card({ title, value }: { title: string; value: string | number }) {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="text-sm text-gray-500 mb-1">{title}</div>
      <div className="text-3xl font-bold text-blue-700">{value}</div>
    </div>
  );
}
