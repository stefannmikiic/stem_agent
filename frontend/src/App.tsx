import { useEffect, useMemo, useState, type ChangeEvent } from 'react';
import { demoSnapshot } from './data/demoState';
import { fetchDashboardState, runBackendPipeline } from './lib/api';
import type { DashboardSnapshot, LearnedRulesState, MemoryEntry, PipelineStageState } from './types';

const emptyRules: LearnedRulesState = {
  by_category: {},
  all_rules: [],
  rule_hit_count: {},
};

const stageStateLabels: Record<PipelineStageState, string> = {
  complete: 'Complete',
  active: 'Active',
  pending: 'Pending',
  warning: 'Warning',
};

type BackendStatus = 'connecting' | 'online' | 'offline' | 'running';

function countIssues(memory: MemoryEntry[]) {
  return memory.reduce(
    (accumulator, entry) => {
      if (entry.issues.includes('pass')) accumulator.pass += 1;
      if (entry.issues.includes('fail')) accumulator.fail += 1;
      if (entry.issues.includes('error')) accumulator.error += 1;
      return accumulator;
    },
    { pass: 0, fail: 0, error: 0 },
  );
}

function flattenRuleCategories(rules: LearnedRulesState) {
  return Object.entries(rules.by_category).flatMap(([category, categoryRules]) =>
    categoryRules.map((rule) => ({ ...rule, category })),
  );
}

function summarizeStage(state: PipelineStageState) {
  if (state === 'complete') return 'Done';
  if (state === 'active') return 'Running';
  if (state === 'warning') return 'Needs attention';
  return 'Waiting';
}

function importJsonFile(file: File, onLoad: (value: unknown) => void, onError: (message: string) => void) {
  const reader = new FileReader();
  reader.onload = () => {
    try {
      const text = String(reader.result ?? '');
      onLoad(JSON.parse(text));
    } catch {
      onError(`Could not parse ${file.name}.`);
    }
  };
  reader.onerror = () => onError(`Could not read ${file.name}.`);
  reader.readAsText(file);
}

function formatCompactBlock(value: string, maxLength: number) {
  if (value.length <= maxLength) return value;
  return `${value.slice(0, maxLength - 1)}...`;
}

function Badge({ children }: { children: string }) {
  return <span className="badge">{children}</span>;
}

function StatCard({ label, value, caption }: { label: string; value: string; caption: string }) {
  return (
    <article className="stat-card">
      <span className="stat-label">{label}</span>
      <strong className="stat-value">{value}</strong>
      <span className="stat-caption">{caption}</span>
    </article>
  );
}

function SectionTitle({ eyebrow, title, description }: { eyebrow: string; title: string; description: string }) {
  return (
    <header className="section-title">
      <span className="eyebrow">{eyebrow}</span>
      <h2>{title}</h2>
      <p>{description}</p>
    </header>
  );
}

export default function App() {
  const [snapshot, setSnapshot] = useState<DashboardSnapshot>(demoSnapshot);
  const [notice, setNotice] = useState('Demo data loaded. Connecting to backend...');
  const [sourceLabel, setSourceLabel] = useState('Demo snapshot');
  const [backendStatus, setBackendStatus] = useState<BackendStatus>('connecting');

  useEffect(() => {
    let active = true;

    fetchDashboardState()
      .then((data) => {
        if (!active) return;
        setSnapshot(data);
        setSourceLabel(data.metadata?.source ?? 'Backend');
        setNotice('Connected to backend snapshot.');
        setBackendStatus('online');
      })
      .catch(() => {
        if (!active) return;
        setBackendStatus('offline');
        setNotice('Backend is offline. Showing demo data.');
      });

    return () => {
      active = false;
    };
  }, []);

  const memory = snapshot.memory ?? [];
  const rules = snapshot.learnedRules ?? emptyRules;
  const issueTotals = countIssues(memory);
  const allRules = useMemo(() => flattenRuleCategories(rules), [rules]);
  const totalRules = rules.all_rules.length;
  const recentMemory = memory.slice(0, 3);
  const topRules = [...allRules].sort((left, right) => right.priority - left.priority).slice(0, 3);
  const completedStages = snapshot.stages.filter((stage) => stage.state === 'complete').length;
  const healthScore =
    typeof snapshot.metadata?.score === 'number'
      ? Math.max(0, Math.min(100, snapshot.metadata.score))
      : Math.max(0, Math.min(100, 60 + issueTotals.pass * 7 - issueTotals.fail * 12 - issueTotals.error * 15));

  function applySnapshot(candidate: unknown, origin: string) {
    if (!candidate || typeof candidate !== 'object') {
      setNotice(`${origin} is not a valid JSON object.`);
      return;
    }

    if (Array.isArray(candidate)) {
      setSnapshot((previous) => ({ ...previous, memory: candidate as MemoryEntry[] }));
      setNotice(`Loaded memory from ${origin}.`);
      setSourceLabel(origin);
      return;
    }

    const payload = candidate as Partial<DashboardSnapshot> & {
      learned_rules?: LearnedRulesState;
      learnedRules?: LearnedRulesState;
    };

    if (payload.title && payload.subtitle && payload.focus && payload.strategy && payload.stages && payload.memory && payload.learnedRules) {
      setSnapshot(payload as DashboardSnapshot);
      setNotice(`Loaded full dashboard snapshot from ${origin}.`);
      setSourceLabel(origin);
      return;
    }

    if (payload.memory && Array.isArray(payload.memory)) {
      setSnapshot((previous) => ({ ...previous, memory: payload.memory as MemoryEntry[] }));
    }

    const loadedRules = payload.learned_rules ?? payload.learnedRules;
    if (loadedRules && Array.isArray(loadedRules.all_rules) && loadedRules.by_category) {
      setSnapshot((previous) => ({ ...previous, learnedRules: loadedRules }));
      setNotice(`Loaded rules from ${origin}.`);
      setSourceLabel(origin);
      return;
    }

    if (payload.strategy || payload.stages || payload.focus) {
      setSnapshot((previous) => ({ ...previous, ...(payload as Partial<DashboardSnapshot>) }));
      setNotice(`Loaded snapshot fragment from ${origin}.`);
      setSourceLabel(origin);
      return;
    }

    setNotice(`${origin} did not match the expected memory or rules schema.`);
  }

  async function refreshFromBackend() {
    setBackendStatus('connecting');
    setNotice('Refreshing live backend snapshot...');

    try {
      const data = await fetchDashboardState();
      setSnapshot(data);
      setSourceLabel(data.metadata?.source ?? 'Backend');
      setNotice('Live backend snapshot refreshed.');
      setBackendStatus('online');
    } catch {
      setBackendStatus('offline');
      setNotice('Could not reach backend. Showing the last available data.');
    }
  }

  async function runBackend() {
    setBackendStatus('running');
    setNotice('Running backend pipeline...');

    try {
      const data = await runBackendPipeline();
      setSnapshot(data);
      setSourceLabel(data.metadata?.source ?? 'Backend run');
      setNotice('Backend pipeline finished and state refreshed.');
      setBackendStatus('online');
    } catch {
      setBackendStatus('offline');
      setNotice('Pipeline run failed or backend is unavailable.');
    }
  }

  function handleFileImport(kind: 'memory' | 'rules' | 'snapshot') {
    return (event: ChangeEvent<HTMLInputElement>) => {
      const file = event.target.files?.[0];
      if (!file) return;

      importJsonFile(
        file,
        (candidate) => {
          if (kind === 'memory' && Array.isArray(candidate)) {
            setSnapshot((previous) => ({ ...previous, memory: candidate as MemoryEntry[] }));
            setNotice(`Loaded ${file.name} as error memory.`);
            setSourceLabel(file.name);
            return;
          }

          if (kind === 'rules' && candidate && typeof candidate === 'object') {
            const payload = candidate as { learned_rules?: LearnedRulesState; learnedRules?: LearnedRulesState };
            const loadedRules = payload.learned_rules ?? payload.learnedRules ?? (candidate as LearnedRulesState);
            if (loadedRules && Array.isArray(loadedRules.all_rules) && loadedRules.by_category) {
              setSnapshot((previous) => ({ ...previous, learnedRules: loadedRules }));
              setNotice(`Loaded ${file.name} as learned rules.`);
              setSourceLabel(file.name);
              return;
            }
          }

          if (kind === 'snapshot') {
            applySnapshot(candidate, file.name);
            return;
          }

          applySnapshot(candidate, file.name);
        },
        (message) => setNotice(message),
      );

      event.target.value = '';
    };
  }

  function resetDemo() {
    setSnapshot(demoSnapshot);
    setNotice('Demo snapshot restored.');
    setSourceLabel('Demo snapshot');
    setBackendStatus('offline');
  }

  function exportSnapshot() {
    const payload = {
      ...snapshot,
      exported_at: new Date().toISOString(),
      source: sourceLabel,
    };

    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'stem-agent-snapshot.json';
    link.click();
    URL.revokeObjectURL(url);
    setNotice('Exported current dashboard snapshot.');
  }

  const backendBadge =
    backendStatus === 'online'
      ? 'Backend online'
      : backendStatus === 'running'
        ? 'Backend running'
        : backendStatus === 'connecting'
          ? 'Connecting'
          : 'Backend offline';

  return (
    <div className="app-shell">
      <div className="orb orb-a" />
      <div className="orb orb-b" />

      <main className="app-frame">
        <section className="hero panel">
          <div className="hero-copy">
            <span className="eyebrow">React front end</span>
            <h1>{snapshot.title}</h1>
            <p className="hero-text">{snapshot.subtitle}</p>
            <div className="hero-pills">
              <Badge>{sourceLabel}</Badge>
              <Badge>{backendBadge}</Badge>
              <Badge>{healthScore >= 70 ? 'Healthy' : 'Watchlist'}</Badge>
              <Badge>{`${completedStages} stages complete`}</Badge>
            </div>
            <p className="hero-focus">{snapshot.focus}</p>
          </div>

          <div className="hero-actions">
            <button className="primary-button" type="button" onClick={runBackend}>
              Run backend pipeline
            </button>
            <button className="secondary-button" type="button" onClick={refreshFromBackend}>
              Refresh live state
            </button>
            <button className="secondary-button" type="button" onClick={resetDemo}>
              Reset demo data
            </button>
            <button className="secondary-button" type="button" onClick={exportSnapshot}>
              Export snapshot
            </button>
            <label className="file-button">
              Import memory JSON
              <input type="file" accept=".json,application/json" onChange={handleFileImport('memory')} />
            </label>
            <label className="file-button">
              Import rules JSON
              <input type="file" accept=".json,application/json" onChange={handleFileImport('rules')} />
            </label>
            <label className="file-button">
              Import snapshot JSON
              <input type="file" accept=".json,application/json" onChange={handleFileImport('snapshot')} />
            </label>
            <p className="notice">{notice}</p>
          </div>
        </section>

        <section className="metrics-grid">
          <StatCard label="Health score" value={`${healthScore}/100`} caption="Balance between pass, fail, and error signals." />
          <StatCard label="Passed runs" value={`${issueTotals.pass}`} caption="Recent snapshots marked as successful." />
          <StatCard label="Failures" value={`${issueTotals.fail}`} caption="Snapshots that exposed a logic or spec mismatch." />
          <StatCard label="Rules learned" value={`${totalRules}`} caption="Reusable rules extracted from prior failures." />
        </section>

        <section className="content-grid">
          <div className="stack">
            <article className="panel">
              <SectionTitle
                eyebrow="Pipeline"
                title="Execution flow"
                description="The app turns a raw strategy into tests, runs pytest, extracts rules, and only then considers an auto-fix."
              />
              <div className="timeline">
                {snapshot.stages.map((stage, index) => (
                  <div className="timeline-item" key={stage.label}>
                    <div className={`timeline-dot state-${stage.state}`} />
                    <div className="timeline-copy">
                      <div className="timeline-head">
                        <strong>{stage.label}</strong>
                        <span>{stageStateLabels[stage.state]}</span>
                      </div>
                      <p>{stage.detail}</p>
                      <small>{summarizeStage(stage.state)} at step {index + 1}.</small>
                    </div>
                  </div>
                ))}
              </div>
            </article>

            <article className="panel">
              <SectionTitle
                eyebrow="Strategy"
                title="Current test strategy"
                description="This is the logical backbone that the React UI surfaces: skills, ordered steps, and the current run context."
              />
              <div className="pill-row">
                {snapshot.strategy.skills.map((skill) => (
                  <Badge key={skill}>{skill}</Badge>
                ))}
              </div>
              <ol className="step-list">
                {snapshot.strategy.steps.map((step) => (
                  <li key={step.step}>
                    <span className="step-index">0{step.step}</span>
                    <p>{step.description}</p>
                  </li>
                ))}
              </ol>
            </article>
          </div>

          <aside className="stack">
            <article className="panel glow-panel">
              <SectionTitle
                eyebrow="Signal"
                title="Run summary"
                description="A quick read on what the agent is seeing now, without scrolling through raw logs first."
              />
              <div className="signal-bars">
                <div>
                  <span>Pass</span>
                  <div className="bar"><i style={{ width: `${Math.max(10, issueTotals.pass * 18)}%` }} /></div>
                </div>
                <div>
                  <span>Fail</span>
                  <div className="bar"><i style={{ width: `${Math.max(10, issueTotals.fail * 18)}%` }} /></div>
                </div>
                <div>
                  <span>Error</span>
                  <div className="bar"><i style={{ width: `${Math.max(10, issueTotals.error * 18)}%` }} /></div>
                </div>
              </div>
              <div className="inline-summary">
                <span>Recent memory entries: {memory.length}</span>
                <span>Rules by category: {Object.keys(rules.by_category).length}</span>
              </div>
            </article>

            <article className="panel">
              <SectionTitle
                eyebrow="Rules"
                title="Top learned rules"
                description="These are the strongest reusable rules extracted from failures and fed back into the pipeline."
              />
              <div className="rule-list">
                {topRules.map((rule) => (
                  <article className="rule-card" key={`${rule.category}-${rule.rule}`}>
                    <div className="rule-card__top">
                      <Badge>{rule.category}</Badge>
                      <span>Priority {rule.priority}</span>
                    </div>
                    <h3>{rule.rule}</h3>
                    <p>{formatCompactBlock(rule.check_method, 110)}</p>
                    <small>{rule.applies_to}</small>
                  </article>
                ))}
              </div>
            </article>
          </aside>
        </section>

        <section className="content-grid bottom-grid">
          <article className="panel">
            <SectionTitle
              eyebrow="Memory"
              title="Recent failures"
              description="These snapshots provide the feedback loop that drives the learning layer."
            />
            <div className="memory-list">
              {recentMemory.map((entry) => (
                <article className="memory-card" key={`${entry.time}-${entry.issues.join('-')}`}>
                  <div className="memory-card__top">
                    <strong>{entry.time}</strong>
                    <div className="pill-row compact">
                      {entry.issues.map((issue) => (
                        <Badge key={issue}>{issue}</Badge>
                      ))}
                    </div>
                  </div>
                  <p>{formatCompactBlock(entry.output, 160)}</p>
                </article>
              ))}
            </div>
          </article>

          <article className="panel">
            <SectionTitle
              eyebrow="Context"
              title="Loaded dataset"
              description="Import either error_memory.json or learned_rules.json from the Python side to keep the dashboard in sync."
            />
            <div className="dataset-list">
              <div>
                <span>Source</span>
                <strong>{sourceLabel}</strong>
              </div>
              <div>
                <span>Memory entries</span>
                <strong>{memory.length}</strong>
              </div>
              <div>
                <span>Total rules</span>
                <strong>{totalRules}</strong>
              </div>
              <div>
                <span>Categories</span>
                <strong>{Object.keys(rules.by_category).length}</strong>
              </div>
            </div>
            <div className="code-panel">
              <h3>Current focus</h3>
              <pre>{snapshot.focus}</pre>
            </div>
          </article>
        </section>
      </main>
    </div>
  );
}
