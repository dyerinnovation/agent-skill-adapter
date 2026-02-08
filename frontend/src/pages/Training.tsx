import { useState } from "react";
import { useApi } from "../hooks/useApi";
import { fetchSkills, listTrainingJobs, startTraining } from "../api/client";

export default function Training() {
  const { data: skills } = useApi(fetchSkills);
  const { data: jobs, loading, error, refetch } = useApi(listTrainingJobs);
  const [selectedSkills, setSelectedSkills] = useState<string[]>([]);
  const [epochs, setEpochs] = useState(3);
  const [lr, setLr] = useState(0.001);
  const [submitting, setSubmitting] = useState(false);

  const handleStart = async () => {
    if (selectedSkills.length === 0) return;
    setSubmitting(true);
    try {
      await startTraining({ skill_ids: selectedSkills, epochs, learning_rate: lr });
      refetch();
      setSelectedSkills([]);
    } catch {
      // error handled by UI
    } finally {
      setSubmitting(false);
    }
  };

  const toggleSkill = (id: string) =>
    setSelectedSkills((prev) =>
      prev.includes(id) ? prev.filter((s) => s !== id) : [...prev, id]
    );

  const statusColor: Record<string, string> = {
    pending: "bg-yellow-100 text-yellow-800",
    running: "bg-blue-100 text-blue-800",
    completed: "bg-green-100 text-green-800",
    failed: "bg-red-100 text-red-800",
  };

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-6">Training</h1>

      <div className="bg-white rounded-lg shadow p-6 mb-8">
        <h2 className="text-lg font-semibold mb-4">Start New Training</h2>
        {skills && (
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">Select Skills</label>
            <div className="flex flex-wrap gap-2">
              {skills.map((s) => (
                <button
                  key={s.skill_id}
                  onClick={() => toggleSkill(s.skill_id)}
                  className={`px-3 py-1 rounded text-sm border ${
                    selectedSkills.includes(s.skill_id)
                      ? "bg-blue-600 text-white border-blue-600"
                      : "bg-white text-gray-700 border-gray-300 hover:border-blue-400"
                  }`}
                >
                  {s.name}
                </button>
              ))}
            </div>
          </div>
        )}
        <div className="flex gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">Epochs</label>
            <input type="number" value={epochs} onChange={(e) => setEpochs(+e.target.value)} className="mt-1 w-24 border rounded px-2 py-1" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Learning Rate</label>
            <input type="number" step="0.0001" value={lr} onChange={(e) => setLr(+e.target.value)} className="mt-1 w-32 border rounded px-2 py-1" />
          </div>
        </div>
        <button
          onClick={handleStart}
          disabled={submitting || selectedSkills.length === 0}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
        >
          {submitting ? "Starting..." : "Start Training"}
        </button>
      </div>

      <h2 className="text-lg font-semibold mb-4">Training Jobs</h2>
      {loading && <p className="text-gray-500">Loading...</p>}
      {error && <p className="text-red-600">Error: {error}</p>}
      {jobs && (
        <table className="w-full bg-white rounded-lg shadow text-sm">
          <thead className="bg-gray-100 text-left">
            <tr>
              <th className="px-4 py-3">Job ID</th>
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3">Progress</th>
              <th className="px-4 py-3">Started</th>
            </tr>
          </thead>
          <tbody>
            {jobs.map((j) => (
              <tr key={j.job_id} className="border-t">
                <td className="px-4 py-3 font-mono text-xs">{j.job_id}</td>
                <td className="px-4 py-3">
                  <span className={`px-2 py-1 rounded text-xs font-medium ${statusColor[j.status] ?? ""}`}>
                    {j.status}
                  </span>
                </td>
                <td className="px-4 py-3">{j.progress != null ? `${j.progress}%` : "—"}</td>
                <td className="px-4 py-3">{j.started_at ?? "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
