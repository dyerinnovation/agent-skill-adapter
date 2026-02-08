import { useApi } from "../hooks/useApi";
import { getEvalResults } from "../api/client";

export default function Evaluation() {
  const { data: results, loading, error } = useApi(getEvalResults);

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-6">Evaluation Results</h1>
      {loading && <p className="text-gray-500">Loading...</p>}
      {error && <p className="text-red-600">Error: {error}</p>}
      {results && results.length === 0 && <p className="text-gray-500">No evaluation results yet.</p>}
      {results && results.map((r) => (
        <div key={r.eval_id} className="bg-white rounded-lg shadow p-6 mb-4">
          <div className="flex justify-between items-center mb-3">
            <h2 className="text-lg font-semibold">{r.skill_name}</h2>
            <span className="text-2xl font-bold text-blue-700">{(r.overall_score * 100).toFixed(1)}%</span>
          </div>
          <div className="text-xs text-gray-400 mb-3">{r.evaluated_at}</div>
          <div className="space-y-2">
            {r.rubric_scores.map((rs) => (
              <div key={rs.name} className="flex items-center gap-3">
                <span className="w-40 text-sm text-gray-700">{rs.name}</span>
                <div className="flex-1 bg-gray-200 rounded-full h-3">
                  <div
                    className="bg-blue-600 h-3 rounded-full"
                    style={{ width: `${rs.score * 100}%` }}
                  />
                </div>
                <span className="text-sm text-gray-600 w-14 text-right">{(rs.score * 100).toFixed(0)}%</span>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
