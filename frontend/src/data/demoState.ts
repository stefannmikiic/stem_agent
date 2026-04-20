import type { DashboardSnapshot } from '../types';

export const demoSnapshot: DashboardSnapshot = {
  title: 'STEM Agent Control Center',
  subtitle: 'A React dashboard for the self-evolving QA loop, with memory, rules, and run history in one place.',
  focus: 'Best recent run: 62 passed, 0 failed, 0 errors',
  strategy: {
    skills: ['Failure analysis', 'Spec-guided test design', 'Rule extraction', 'Auto-fix validation'],
    steps: [
      { step: 1, description: 'Generate a target-aware test strategy from the current QA task and memory.' },
      { step: 2, description: 'Run pytest and capture summary counts, collection errors, and failure context.' },
      { step: 3, description: 'Extract reusable learning rules from failures and persist them to memory.' },
      { step: 4, description: 'Apply code fixes only when the failure is in the sample code, not the generated tests.' },
    ],
  },
  stages: [
    { label: 'Strategy', detail: 'Build the next testing angle from prior failures.', state: 'complete' },
    { label: 'Generation', detail: 'Create pytest cases aligned with FUNCTION_SPEC.md.', state: 'complete' },
    { label: 'Execution', detail: 'Run the generated suite and collect counts.', state: 'complete' },
    { label: 'Learning', detail: 'Promote new failures into reusable rules.', state: 'active' },
    { label: 'Fixing', detail: 'Patch sample code only when the evidence points there.', state: 'pending' },
  ],
  memory: [
    {
      time: '2026-04-20 00:22:52',
      issues: ['pass'],
      output: '62 passed in 0.09s',
    },
    {
      time: '2026-04-20 00:22:30',
      issues: ['fail'],
      output: '3 failures in generated tests. One case exposed a mismatch in expected return type.',
    },
    {
      time: '2026-04-20 00:16:37',
      issues: ['error'],
      output: 'NameError during collection because dict_keys was referenced without an import.',
    },
    {
      time: '2026-04-20 00:13:15',
      issues: ['fail', 'error'],
      output: 'Collection error surfaced a walrus operator syntax issue in generated tests.',
    },
  ],
  learnedRules: {
    by_category: {
      type_check: [
        {
          rule: 'Validate sequence-like inputs before subscript access and reject unsupported containers explicitly.',
          category: 'type_check',
          applies_to: 'get_element',
          check_method: 'Assert supported types in tests and add a TypeError branch for unsupported collections.',
          priority: 9,
          hit_count: 4,
          discovered_at: '1776637352.1122146',
        },
        {
          rule: 'Confirm result type assertions match the actual contract, especially for exact-vs-inexact division.',
          category: 'type_check',
          applies_to: 'divide',
          check_method: 'Use precise pytest assertions for int versus float outcomes.',
          priority: 8,
          hit_count: 3,
          discovered_at: '1776636957.4836864',
        },
      ],
      syntax: [
        {
          rule: 'Avoid assignment expressions in unsupported syntax positions during test generation.',
          category: 'syntax',
          applies_to: 'test_generated.py',
          check_method: 'Lint generated code for invalid walrus usage before running pytest.',
          priority: 8,
          hit_count: 2,
          discovered_at: '1776636552.493391',
        },
      ],
    },
    all_rules: [
      {
        rule: 'Validate sequence-like inputs before subscript access and reject unsupported containers explicitly.',
        category: 'type_check',
        applies_to: 'get_element',
        check_method: 'Assert supported types in tests and add a TypeError branch for unsupported collections.',
        priority: 9,
        hit_count: 4,
        discovered_at: '1776637352.1122146',
      },
      {
        rule: 'Confirm result type assertions match the actual contract, especially for exact-vs-inexact division.',
        category: 'type_check',
        applies_to: 'divide',
        check_method: 'Use precise pytest assertions for int versus float outcomes.',
        priority: 8,
        hit_count: 3,
        discovered_at: '1776636957.4836864',
      },
      {
        rule: 'Avoid assignment expressions in unsupported syntax positions during test generation.',
        category: 'syntax',
        applies_to: 'test_generated.py',
        check_method: 'Lint generated code for invalid walrus usage before running pytest.',
        priority: 8,
        hit_count: 2,
        discovered_at: '1776636552.493391',
      },
    ],
    rule_hit_count: {},
  },
};
