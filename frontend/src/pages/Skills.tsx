import { useState } from "react";
import { useApi } from "../hooks/useApi";
import { fetchSkills } from "../api/client";
import type { SkillInfo } from "../types";

export default function Skills() {
  const { data: skills, loading, error } = useApi(fetchSkills);
  const [selected, setSelected] = useState<SkillInfo | null>(null);

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-6">Skills</h1>
      {loading && <p className="text-gray-500">Loading...</p>}
      {error && <p className="text-red-600">Error: {error}</p>}
      {skills && (
        <table className="w-full bg-white rounded-lg shadow text-sm">
          <thead className="bg-gray-100 text-left">
            <tr>
              <th className="px-4 py-3">Name</th>
              <th className="px-4 py-3">Description</th>
              <th className="px-4 py-3">Rubric Items</th>
              <th className="px-4 py-3">Last Trained</th>
              <th className="px-4 py-3"></th>
            </tr>
          </thead>
          <tbody>
            {skills.map((s) => (
              <tr key={s.skill_id} className="border-t">
                <td className="px-4 py-3 font-medium">{s.name}</td>
                <td className="px-4 py-3 text-gray-600">{s.description}</td>
                <td className="px-4 py-3">{s.rubric.length}</td>
                <td className="px-4 py-3">{s.last_trained ?? "Never"}</td>
                <td className="px-4 py-3">
                  <button
                    onClick={() => setSelected(selected?.skill_id === s.skill_id ? null : s)}
                    className="text-blue-600 hover:underline"
                  >
                    {selected?.skill_id === s.skill_id ? "Hide" : "Details"}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
      {selected && (
        <div className="mt-6 bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold mb-3">{selected.name} - Rubric</h2>
          <ul className="space-y-2">
            {selected.rubric.map((r) => (
              <li key={r.name} className="flex justify-between border-b pb-2">
                <div>
                  <span className="font-medium">{r.name}</span>
                  <span className="text-gray-500 ml-2 text-sm">{r.description}</span>
                </div>
                <span className="text-gray-700">Weight: {r.weight}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
