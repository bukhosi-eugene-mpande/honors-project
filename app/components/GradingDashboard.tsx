"use client";
import React, { useEffect, useMemo, useState } from "react";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, BarChart, Bar, Legend, CartesianGrid, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar } from "recharts";

/**
 * GradingDashboard
 * --------------------------------------------------------------
 * A single-file React UI to visualize overall and per-question stats
 * from your LLM grading pipeline. Drop into any React app. Uses Tailwind
 * for styling and Recharts for graphs (both widely available).
 *
 * Props:
 *  - data?: StatsData            // pass the JSON object directly
 *  - dataUrl?: string            // OR URL to a JSON file (e.g., S3 presigned URL)
 *  - title?: string              // optional page title
 *
 * If both data and dataUrl are omitted, the component renders a demo using
 * SAMPLE_DATA below. Replace SAMPLE_DATA with your JSON or provide dataUrl.
 */

// ------------------ Types ------------------

type AgreementMap = Record<string, number | null>;

interface PerQuestionEntry {
  question_id: number;
  question: string;
  max_point: number | null;
  counts: {
    answers_n: number;
    dropped_failures?: number;
  };
  scores: {
    means: {
      score_me: number | null;
      score_other: number | null;
      score_avg: number | null;
      llm_score: number | null;
    };
    llm_quantiles: Record<string, number>;
    llm_min: number | null;
    llm_max: number | null;
    agreement_and_errors: {
      pearson_llm_vs_score_me: number | null;
      pearson_llm_vs_score_other: number | null;
      pearson_llm_vs_score_avg: number | null;
      mae_llm_vs_score_me: number | null;
      mae_llm_vs_score_other: number | null;
      mae_llm_vs_score_avg: number | null;
      rmse_llm_vs_score_me: number | null;
      rmse_llm_vs_score_other: number | null;
      rmse_llm_vs_score_avg: number | null;
      agree_score_me_within: AgreementMap;
      agree_score_other_within: AgreementMap;
      agree_score_avg_within: AgreementMap;
    };
  };
  reference_similarity?: {
    desired_vs_llm_avg_jaccard?: number | null;
    desired_vs_llm_max_jaccard?: number | null;
    llm_answer_pairwise_avg_jaccard?: number | null;
    desired_len_tokens?: number | null;
    llm_len_tokens_avg?: number | null;
    llm_count?: number | null;
  };
}

interface StatsData {
  overall: {
    counts: {
      total_answers: number;
      total_questions: number;
      dropped_failures_total?: number;
    };
    means: {
      score_me: number | null;
      score_other: number | null;
      score_avg: number | null;
      llm_score: number | null;
    };
    pearson_llm_vs_score_me: number | null;
    mae_llm_vs_score_me: number | null;
    rmse_llm_vs_score_me: number | null;
    pearson_llm_vs_score_other: number | null;
    mae_llm_vs_score_other: number | null;
    rmse_llm_vs_score_other: number | null;
    pearson_llm_vs_score_avg: number | null;
    mae_llm_vs_score_avg: number | null;
    rmse_llm_vs_score_avg: number | null;
    reference_similarity?: {
      desired_vs_llm_avg_jaccard_mean?: number | null;
      desired_vs_llm_max_jaccard_mean?: number | null;
      llm_answer_pairwise_avg_jaccard_mean?: number | null;
      desired_len_tokens_mean?: number | null;
      llm_len_tokens_avg_mean?: number | null;
    };
  };
  per_question: PerQuestionEntry[];
  inputs?: any;
}

// ------------------ Sample (replace or override via props) ------------------

const SAMPLE_DATA: StatsData = {
  overall: {
    counts: {
      total_answers: 1889,
      total_questions: 81,
      dropped_failures_total: 384,
    },
    means: {
      score_me: 3.9174166225516145,
      score_other: 4.4016675489677075,
      score_avg: 4.159542085759661,
      llm_score: 2.3080995235574377,
    },
    pearson_llm_vs_score_me: 0.4713754247963934,
    mae_llm_vs_score_me: 1.8046585494970884,
    rmse_llm_vs_score_me: 2.152595783636342,
    pearson_llm_vs_score_other: 0.3625746268985321,
    mae_llm_vs_score_other: 2.1345950238221283,
    rmse_llm_vs_score_other: 2.4306078838468634,
    pearson_llm_vs_score_avg: 0.47740125897368535,
    mae_llm_vs_score_avg: 1.8967046056114347,
    rmse_llm_vs_score_avg: 2.19962090373987,
    reference_similarity: {
      desired_vs_llm_avg_jaccard_mean: 0.1294866613355469,
      desired_vs_llm_max_jaccard_mean: 0.13974429181645573,
      llm_answer_pairwise_avg_jaccard_mean: 0.6943865601401152,
      desired_len_tokens_mean: 15.530864197530864,
      llm_len_tokens_avg_mean: 73.5925925925926,
    },
  },
  per_question: [
    {
      question_id: 1,
      question: "What is the role of a prototype program in problem solving?",
      max_point: 5.0,
      counts: { answers_n: 22, dropped_failures: 7 },
      scores: {
        means: {
          score_me: 3.6363636363636362,
          score_other: 3.409090909090909,
          score_avg: 3.522727272727273,
          llm_score: 2.1818181818181817,
        },
        llm_quantiles: { "0.1": 1.1, "0.25": 2.0, "0.5": 2.0, "0.75": 3.0, "0.9": 3.0 },
        llm_min: 1.0,
        llm_max: 3.0,
        agreement_and_errors: {
          pearson_llm_vs_score_me: 0.444067137305859,
          pearson_llm_vs_score_other: 0.17184412710591615,
          pearson_llm_vs_score_avg: 0.320151404900689,
          mae_llm_vs_score_me: 1.4545454545454546,
          mae_llm_vs_score_other: 1.5,
          mae_llm_vs_score_avg: 1.4318181818181819,
          rmse_llm_vs_score_me: 1.8829377433825436,
          rmse_llm_vs_score_other: 1.8708286933869707,
          rmse_llm_vs_score_avg: 1.8309212782838937,
          agree_score_me_within: { "0.25": 0.3181818181818182, "0.5": 0.3181818181818182, "1.0": 0.5 },
          agree_score_other_within: { "0.25": 0.22727272727272727, "0.5": 0.22727272727272727, "1.0": 0.5454545454545454 },
          agree_score_avg_within: { "0.25": 0.22727272727272727, "0.5": 0.4090909090909091, "1.0": 0.45454545454545453 },
        },
      },
      reference_similarity: {
        desired_vs_llm_avg_jaccard: 0.06557377049180328,
        desired_vs_llm_max_jaccard: 0.06557377049180328,
        llm_answer_pairwise_avg_jaccard: 1.0,
        desired_len_tokens: 11,
        llm_len_tokens_avg: 65.0,
        llm_count: 3,
      },
    },
  ],
};

// ------------------ Small helpers ------------------

function fmt(num?: number | null, digits = 2) {
  if (num === null || num === undefined || Number.isNaN(num)) return "–";
  return Number(num).toFixed(digits);
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="bg-white dark:bg-gray-900 rounded-2xl shadow-sm dark:shadow-lg p-6 border border-gray-100 dark:border-gray-800 transition-colors">
      <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-gray-100">{title}</h2>
      {children}
    </section>
  );
}

function StatCard({ label, value, hint }: { label: string; value: string; hint?: string }) {
  return (
    <div className="rounded-2xl border border-gray-100 dark:border-gray-800 bg-gray-50 dark:bg-gray-800 p-4 transition-colors">
      <div className="text-sm text-gray-500 dark:text-gray-400">{label}</div>
      <div className="text-2xl font-semibold text-gray-900 dark:text-gray-100">{value}</div>
      {hint && <div className="text-xs text-gray-400 dark:text-gray-500 mt-1">{hint}</div>}
    </div>
  );
}

// ------------------ Main component ------------------

export default function GradingDashboard({ data, dataUrl, title = "LLM Grading Dashboard" }: { data?: StatsData; dataUrl?: string; title?: string }) {
  const [json, setJson] = useState<StatsData | null>(data || null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [qFilter, setQFilter] = useState<string>("");
  const [sortKey, setSortKey] = useState<string>("question_id");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("asc");
  const [isDarkMode, setIsDarkMode] = useState<boolean>(false);

  useEffect(() => {
    if (!data && dataUrl) {
      setLoading(true);
      fetch(dataUrl)
        .then(r => {
          if (!r.ok) throw new Error(`HTTP ${r.status}`);
          return r.json();
        })
        .then(setJson)
        .catch(e => setError(e.message))
        .finally(() => setLoading(false));
    }
  }, [data, dataUrl]);

  useEffect(() => {
    // Check for saved theme preference or default to system preference
    const savedTheme = localStorage.getItem('theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const shouldUseDark = savedTheme === 'dark' || (!savedTheme && prefersDark);
    
    setIsDarkMode(shouldUseDark);
    
    if (shouldUseDark) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, []);

  const toggleDarkMode = () => {
    const newDarkMode = !isDarkMode;
    setIsDarkMode(newDarkMode);
    localStorage.setItem('theme', newDarkMode ? 'dark' : 'light');
    
    if (newDarkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  };

  const model: StatsData = json || SAMPLE_DATA;

  // Derived data for charts
  const meanScoreBars = useMemo(() => (
    [
      { name: "Score (Me)", value: model.overall.means.score_me },
      { name: "Score (Other)", value: model.overall.means.score_other },
      { name: "Score (Human Avg)", value: model.overall.means.score_avg },
      { name: "Score (LLM)", value: model.overall.means.llm_score },
    ]
  ), [model]);

  const corrLines = useMemo(() => (
    [
      { name: "LLM vs Me", value: model.overall.pearson_llm_vs_score_me },
      { name: "LLM vs Other", value: model.overall.pearson_llm_vs_score_other },
      { name: "LLM vs Human Avg", value: model.overall.pearson_llm_vs_score_avg },
    ]
  ), [model]);

  const errorBars = useMemo(() => (
    [
      { metric: "MAE vs Me", value: model.overall.mae_llm_vs_score_me },
      { metric: "RMSE vs Me", value: model.overall.rmse_llm_vs_score_me },
      { metric: "MAE vs Other", value: model.overall.mae_llm_vs_score_other },
      { metric: "RMSE vs Other", value: model.overall.rmse_llm_vs_score_other },
      { metric: "MAE vs Avg", value: model.overall.mae_llm_vs_score_avg },
      { metric: "RMSE vs Avg", value: model.overall.rmse_llm_vs_score_avg },
    ]
  ), [model]);

  const filteredQuestions = useMemo(() => {
    const q = (qFilter || "").toLowerCase();
    const rows = [...(model.per_question || [])];
    
    const sorted = rows.sort((a, b) => {
      const dir = sortDir === "asc" ? 1 : -1;
      let A: any;
      let B: any;
      
      // Handle different sort keys
      switch (sortKey) {
        case "question_id":
          A = a.question_id;
          B = b.question_id;
          break;
        case "answers_n":
          A = a.counts.answers_n;
          B = b.counts.answers_n;
          break;
        case "llm_score":
          A = a.scores.means.llm_score;
          B = b.scores.means.llm_score;
          break;
        case "score_avg":
          A = a.scores.means.score_avg;
          B = b.scores.means.score_avg;
          break;
        case "pearson_llm_vs_score_avg":
          A = a.scores.agreement_and_errors.pearson_llm_vs_score_avg;
          B = b.scores.agreement_and_errors.pearson_llm_vs_score_avg;
          break;
        default:
          A = a.question_id;
          B = b.question_id;
      }
      
      // Handle null/undefined values
      if (A === null || A === undefined) A = -Infinity;
      if (B === null || B === undefined) B = -Infinity;
      
      if (A === B) return 0;
      return A > B ? dir : -dir;
    });
    
    if (!q) return sorted;
    return sorted.filter(r => `${r.question_id}`.includes(q) || (r.question || "").toLowerCase().includes(q));
  }, [model, qFilter, sortKey, sortDir]);

  if (loading) return <div className="p-8 text-gray-900 dark:text-gray-100">Loading…</div>;
  if (error) return <div className="p-8 text-red-600 dark:text-red-400">Error: {error}</div>;

  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-950 transition-colors">
      <header className="px-6 py-4 sticky top-0 bg-white/80 dark:bg-gray-900/80 backdrop-blur border-b border-gray-200 dark:border-gray-800 transition-colors">
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">{title}</h1>
            <p className="text-sm text-gray-500 dark:text-gray-400">Visualizing LLM vs Human grading statistics</p>
          </div>
          <button
            onClick={toggleDarkMode}
            className="p-2 rounded-lg bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
            aria-label="Toggle dark mode"
          >
            {isDarkMode ? (
              <svg className="w-5 h-5 text-yellow-500" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z" clipRule="evenodd" />
              </svg>
            ) : (
              <svg className="w-5 h-5 text-gray-700" fill="currentColor" viewBox="0 0 20 20">
                <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z" />
              </svg>
            )}
          </button>
        </div>
      </header>

      <main className="p-6 space-y-6">
        {/* KPI Row */}
        <div className="grid md:grid-cols-4 gap-4">
          <StatCard label="Total Answers" value={`${model.overall.counts.total_answers}`} hint={`Dropped failures: ${model.overall.counts.dropped_failures_total ?? 0}`} />
          <StatCard label="Questions" value={`${model.overall.counts.total_questions}`} />
          <StatCard label="Human Avg" value={fmt(model.overall.means.score_avg)} hint={`Me: ${fmt(model.overall.means.score_me)} · Other: ${fmt(model.overall.means.score_other)}`} />
          <StatCard label="LLM Avg" value={fmt(model.overall.means.llm_score)} />
        </div>

        {/* Charts */}
        <div className="grid lg:grid-cols-3 gap-6">
          <Section title="Mean Scores (Overall)">
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={meanScoreBars}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis domain={[0, 5]} />
                  <Tooltip />
                  <Bar dataKey="value" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </Section>

          <Section title="Correlation (LLM vs Humans)">
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={corrLines}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis domain={[0, 1]} />
                  <Tooltip />
                  <Bar dataKey="value" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </Section>

          <Section title="Errors (Lower is Better)">
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={errorBars}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="metric" hide />
                  <YAxis domain={[0, 5]} />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="value" name="Error" />
                </BarChart>
              </ResponsiveContainer>
              <div className="text-xs text-gray-500 mt-2">Includes MAE and RMSE vs each human score.
              </div>
            </div>
          </Section>
        </div>

        {/* Reference Similarity */}
        <Section title="Reference Similarity (Desired Answer vs LLM References)">
          <div className="grid md:grid-cols-5 gap-4">
            <StatCard label="Avg Jaccard" value={fmt(model.overall.reference_similarity?.desired_vs_llm_avg_jaccard_mean)} />
            <StatCard label="Max Jaccard" value={fmt(model.overall.reference_similarity?.desired_vs_llm_max_jaccard_mean)} />
            <StatCard label="LLM Ref Diversity" value={fmt(model.overall.reference_similarity?.llm_answer_pairwise_avg_jaccard_mean)} hint="Higher = more overlap between refs" />
            <StatCard label="Desired Len (tokens)" value={fmt(model.overall.reference_similarity?.desired_len_tokens_mean, 1)} />
            <StatCard label="LLM Ref Len (tokens)" value={fmt(model.overall.reference_similarity?.llm_len_tokens_avg_mean, 1)} />
          </div>
        </Section>

        {/* Per-question table */}
        <Section title="Per Question">
          <div className="flex flex-col sm:flex-row sm:items-center gap-3 mb-4">
            <input
              type="text"
              placeholder="Search by ID or text…"
              value={qFilter}
              onChange={(e) => setQFilter(e.target.value)}
              className="w-full sm:w-80 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400 px-3 py-2 focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400 focus:border-transparent transition-colors"
            />
            <div className="flex gap-2 items-center">
              <label className="text-sm text-gray-600 dark:text-gray-400">Sort by:</label>
              <select
                value={sortKey}
                onChange={(e) => setSortKey(e.target.value)}
                className="rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 px-3 py-2 focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400 focus:border-transparent transition-colors"
              >
                <option value="question_id">Question ID</option>
                <option value="answers_n">Answers N</option>
                <option value="llm_score">Mean LLM Score</option>
                <option value="score_avg">Mean Human Avg</option>
                <option value="pearson_llm_vs_score_avg">Correlation (LLM vs Human Avg)</option>
              </select>
              <button
                onClick={() => setSortDir(d => (d === "asc" ? "desc" : "asc"))}
                className="rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 px-3 py-2 hover:bg-gray-50 dark:hover:bg-gray-700 focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400 focus:border-transparent transition-colors"
              >{sortDir === "asc" ? "Asc" : "Desc"}</button>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead>
                <tr className="text-left text-gray-500 dark:text-gray-400">
                  <th className="py-2 pr-4">ID</th>
                  <th className="py-2 pr-4">Question</th>
                  <th className="py-2 pr-4">N</th>
                  <th className="py-2 pr-4">Dropped</th>
                  <th className="py-2 pr-4">Human Avg</th>
                  <th className="py-2 pr-4">LLM Avg</th>
                  <th className="py-2 pr-4">Corr (LLM vs Human Avg)</th>
                  <th className="py-2 pr-4">MAE (vs Human Avg)</th>
                  <th className="py-2 pr-4">LLM Min–Max</th>
                </tr>
              </thead>
              <tbody>
                {filteredQuestions.map((q) => {
                  const ag = q.scores.agreement_and_errors;
                  return (
                    <tr key={q.question_id} className="border-t border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors">
                      <td className="py-2 pr-4 font-mono text-gray-900 dark:text-gray-100">{q.question_id}</td>
                      <td className="py-2 pr-4 max-w-3xl">
                        <div className="font-medium text-gray-900 dark:text-gray-100">{q.question}</div>
                        <div className="text-xs text-gray-500 dark:text-gray-400">Max {q.max_point ?? "–"} · Quantiles: {Object.entries(q.scores.llm_quantiles).map(([k,v]) => `${k}:${fmt(v,1)}`).join(" · ")}</div>
                      </td>
                      <td className="py-2 pr-4 text-gray-900 dark:text-gray-100">{q.counts.answers_n}</td>
                      <td className="py-2 pr-4 text-gray-900 dark:text-gray-100">{q.counts.dropped_failures ?? 0}</td>
                      <td className="py-2 pr-4 text-gray-900 dark:text-gray-100">{fmt(q.scores.means.score_avg)}</td>
                      <td className="py-2 pr-4 text-gray-900 dark:text-gray-100">{fmt(q.scores.means.llm_score)}</td>
                      <td className="py-2 pr-4 text-gray-900 dark:text-gray-100">{fmt(ag.pearson_llm_vs_score_avg)}</td>
                      <td className="py-2 pr-4 text-gray-900 dark:text-gray-100">{fmt(ag.mae_llm_vs_score_avg)}</td>
                      <td className="py-2 pr-4 text-gray-900 dark:text-gray-100">{fmt(q.scores.llm_min)}–{fmt(q.scores.llm_max)}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </Section>

        {/* Footer */}
        <div className="text-xs text-gray-500 dark:text-gray-400">
          Inputs: {model.inputs?.questions_s3 ?? ""} · {model.inputs?.graded_prefix_s3 ?? ""}
        </div>
      </main>
    </div>
  );
}
