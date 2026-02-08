// Skill-related types
export interface RubricItem {
  name: string;
  description: string;
  weight: number;
}

export interface SkillInfo {
  skill_id: string;
  name: string;
  description: string;
  rubric: RubricItem[];
  last_trained?: string;
  created_at?: string;
}

// Training-related types
export interface TrainingRequest {
  skill_ids: string[];
  epochs?: number;
  learning_rate?: number;
  batch_size?: number;
}

export interface TrainingJob {
  job_id: string;
  skill_ids: string[];
  status: 'pending' | 'running' | 'completed' | 'failed';
  progress?: number;
  epochs?: number;
  learning_rate?: number;
  batch_size?: number;
  started_at?: string;
  completed_at?: string;
  error?: string;
}

// Evaluation-related types
export interface EvaluationRequest {
  skill_ids: string[];
  test_data_path?: string;
}

export interface RubricScore {
  name: string;
  score: number;
  weight: number;
}

export interface EvalResult {
  eval_id: string;
  skill_id: string;
  skill_name: string;
  overall_score: number;
  rubric_scores: RubricScore[];
  evaluated_at: string;
}

// Dashboard stats
export interface DashboardStats {
  total_skills: number;
  active_training_jobs: number;
  recent_eval_avg_score: number;
}
