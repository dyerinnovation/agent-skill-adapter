import type { SkillInfo, TrainingRequest, TrainingJob, EvaluationRequest, EvalResult, DashboardStats } from '../types';

const BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

export async function fetchJson<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, options);
  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`API error: ${res.status} - ${errorText}`);
  }
  return res.json();
}

// Skills API
export async function fetchSkills(): Promise<SkillInfo[]> {
  return fetchJson<SkillInfo[]>('/skills');
}

export async function fetchSkill(skillId: string): Promise<SkillInfo> {
  return fetchJson<SkillInfo>(`/skills/${skillId}`);
}

// Training API
export async function startTraining(request: TrainingRequest): Promise<TrainingJob> {
  return fetchJson<TrainingJob>('/training/start', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });
}

export async function getTrainingStatus(jobId: string): Promise<TrainingJob> {
  return fetchJson<TrainingJob>(`/training/status/${jobId}`);
}

export async function listTrainingJobs(): Promise<TrainingJob[]> {
  return fetchJson<TrainingJob[]>('/training/jobs');
}

// Evaluation API
export async function runEvaluation(request: EvaluationRequest): Promise<{ eval_id: string }> {
  return fetchJson<{ eval_id: string }>('/evaluation/run', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });
}

export async function getEvalResults(evalId?: string): Promise<EvalResult[]> {
  const path = evalId ? `/evaluation/results/${evalId}` : '/evaluation/results';
  return fetchJson<EvalResult[]>(path);
}

// Dashboard stats
export async function getDashboardStats(): Promise<DashboardStats> {
  return fetchJson<DashboardStats>('/stats/dashboard');
}
