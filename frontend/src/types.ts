export type PipelineStageState = 'complete' | 'active' | 'pending' | 'warning';

export interface PipelineStage {
  label: string;
  detail: string;
  state: PipelineStageState;
}

export interface MemoryEntry {
  time: string;
  issues: string[];
  output: string;
  codeSnapshot?: string;
}

export interface LearnedRule {
  rule: string;
  category: string;
  applies_to: string;
  check_method: string;
  priority: number;
  hit_count: number;
  discovered_at?: string;
  context?: string;
}

export interface LearnedRulesState {
  by_category: Record<string, LearnedRule[]>;
  all_rules: LearnedRule[];
  rule_hit_count: Record<string, number>;
}

export interface StrategyStep {
  step: number;
  description: string;
}

export interface Strategy {
  skills: string[];
  steps: StrategyStep[];
}

export interface DashboardSnapshot {
  title: string;
  subtitle: string;
  focus: string;
  strategy: Strategy;
  stages: PipelineStage[];
  memory: MemoryEntry[];
  learnedRules: LearnedRulesState;
  metadata?: {
    issues?: string[];
    iteration?: number;
    score?: number;
    bestScore?: number;
    source?: string;
  };
}
