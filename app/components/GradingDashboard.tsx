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
      llm_score?: number | null;
      nlp_score?: number | null;
    };
    llm_quantiles?: Record<string, number>;
    nlp_quantiles?: Record<string, number>;
    llm_min?: number | null;
    llm_max?: number | null;
    nlp_min?: number | null;
    nlp_max?: number | null;
    agreement_and_errors: {
      pearson_llm_vs_score_me?: number | null;
      pearson_llm_vs_score_other?: number | null;
      pearson_llm_vs_score_avg?: number | null;
      mae_llm_vs_score_me?: number | null;
      mae_llm_vs_score_other?: number | null;
      mae_llm_vs_score_avg?: number | null;
      rmse_llm_vs_score_me?: number | null;
      rmse_llm_vs_score_other?: number | null;
      rmse_llm_vs_score_avg?: number | null;
      pearson_nlp_vs_score_me?: number | null;
      pearson_nlp_vs_score_other?: number | null;
      pearson_nlp_vs_score_avg?: number | null;
      mae_nlp_vs_score_me?: number | null;
      mae_nlp_vs_score_other?: number | null;
      mae_nlp_vs_score_avg?: number | null;
      rmse_nlp_vs_score_me?: number | null;
      rmse_nlp_vs_score_other?: number | null;
      rmse_nlp_vs_score_avg?: number | null;
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
      llm_score?: number | null;
      nlp_score?: number | null;
    };
    pearson_llm_vs_score_me?: number | null;
    mae_llm_vs_score_me?: number | null;
    rmse_llm_vs_score_me?: number | null;
    pearson_llm_vs_score_other?: number | null;
    mae_llm_vs_score_other?: number | null;
    rmse_llm_vs_score_other?: number | null;
    pearson_llm_vs_score_avg?: number | null;
    mae_llm_vs_score_avg?: number | null;
    rmse_llm_vs_score_avg?: number | null;
    pearson_nlp_vs_score_me?: number | null;
    mae_nlp_vs_score_me?: number | null;
    rmse_nlp_vs_score_me?: number | null;
    pearson_nlp_vs_score_other?: number | null;
    mae_nlp_vs_score_other?: number | null;
    rmse_nlp_vs_score_other?: number | null;
    pearson_nlp_vs_score_avg?: number | null;
    mae_nlp_vs_score_avg?: number | null;
    rmse_nlp_vs_score_avg?: number | null;
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

export default function GradingDashboard({ data, dataUrl, title = "Grading Approach Comparison Dashboard" }: { data?: StatsData; dataUrl?: string; title?: string }) {
  const [json, setJson] = useState<StatsData | null>(data || null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [qFilter, setQFilter] = useState<string>("");
  const [sortKey, setSortKey] = useState<string>("question_id");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("asc");
  const [isDarkMode, setIsDarkMode] = useState<boolean>(false);
  const [selectedApproach, setSelectedApproach] = useState<string>("llm_direct");
  const [allApproachesData, setAllApproachesData] = useState<Record<string, StatsData>>({});

  // Define available approaches
  const approaches = {
    "llm_direct": {
      name: "LLM Direct Grading",
      description: "LLM grades student answers directly",
      dataUrl: "/graded_stats.json",
      color: "#3b82f6"
    },
    "llm_with_nlp": {
      name: "LLM + NLP Grading", 
      description: "LLM generates model answer, then NLP grades against it",
      dataUrl: "/graded_stats/stats_results_llm_with_nlp.json",
      color: "#10b981"
    },
    "model_answer": {
      name: "Model Answer Approach",
      description: "LLM generates model answer, then grades against dataset answer",
      dataUrl: "/graded_stats/stats_results_model_answer.json",
      color: "#f59e0b"
    }
  };

  // Load all approaches data for comparison
  useEffect(() => {
    const loadAllApproaches = async () => {
      setLoading(true);
      const dataPromises = Object.entries(approaches).map(async ([key, approach]) => {
        try {
          const response = await fetch(approach.dataUrl);
          if (!response.ok) throw new Error(`HTTP ${response.status}`);
          const data = await response.json();
          return [key, data];
        } catch (error) {
          console.error(`Error loading ${approach.name}:`, error);
          return [key, null];
        }
      });

      const results = await Promise.all(dataPromises);
      const approachesData: Record<string, StatsData> = {};
      
      results.forEach(([key, data]) => {
        if (data) {
          approachesData[key] = data;
        }
      });

      setAllApproachesData(approachesData);
      setLoading(false);
    };

    // Always load all approaches for comparison
    loadAllApproaches();
  }, [dataUrl]);

  // Set current approach data
  useEffect(() => {
    if (allApproachesData[selectedApproach]) {
      setJson(allApproachesData[selectedApproach]);
    }
  }, [selectedApproach, allApproachesData]);

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

  const model: StatsData = json || {
    overall: {
      counts: { total_answers: 0, total_questions: 0 },
      means: { score_me: 0, score_other: 0, score_avg: 0, llm_score: 0 }
    },
    per_question: []
  };

  // Get the appropriate AI score based on approach
  const getAIScore = () => {
    if (model.overall.means.llm_score !== undefined) return model.overall.means.llm_score;
    if (model.overall.means.nlp_score !== undefined) return model.overall.means.nlp_score;
    return 0;
  };

  const getAIScoreName = () => {
    if (model.overall.means.llm_score !== undefined) return "LLM Score";
    if (model.overall.means.nlp_score !== undefined) return "NLP Score";
    return "AI Score";
  };

  // Derived data for charts
  const meanScoreBars = useMemo(() => (
    [
      { name: "Data Scientist", value: model.overall.means.score_me },
      { name: "Researcher", value: model.overall.means.score_other },
      { name: "Human Average", value: model.overall.means.score_avg },
      { name: getAIScoreName(), value: getAIScore() },
    ]
  ), [model]);

  // Get correlation values based on approach
  const getCorrelationData = () => {
    const aiName = getAIScoreName();
    if (model.overall.pearson_llm_vs_score_me !== undefined) {
      return [
        { name: `${aiName} vs Data Scientist`, value: model.overall.pearson_llm_vs_score_me },
        { name: `${aiName} vs Researcher`, value: model.overall.pearson_llm_vs_score_other },
        { name: `${aiName} vs Human Average`, value: model.overall.pearson_llm_vs_score_avg },
      ];
    }
    if (model.overall.pearson_nlp_vs_score_me !== undefined) {
      return [
        { name: `${aiName} vs Data Scientist`, value: model.overall.pearson_nlp_vs_score_me },
        { name: `${aiName} vs Researcher`, value: model.overall.pearson_nlp_vs_score_other },
        { name: `${aiName} vs Human Average`, value: model.overall.pearson_nlp_vs_score_avg },
      ];
    }
    return [];
  };

  const corrLines = useMemo(() => getCorrelationData(), [model]);

  // Get error values based on approach
  const getErrorData = () => {
    const aiName = getAIScoreName();
    if (model.overall.mae_llm_vs_score_me !== undefined) {
      return [
        { metric: `MAE vs Data Scientist`, value: model.overall.mae_llm_vs_score_me },
        { metric: `RMSE vs Data Scientist`, value: model.overall.rmse_llm_vs_score_me },
        { metric: `MAE vs Researcher`, value: model.overall.mae_llm_vs_score_other },
        { metric: `RMSE vs Researcher`, value: model.overall.rmse_llm_vs_score_other },
        { metric: `MAE vs Human Avg`, value: model.overall.mae_llm_vs_score_avg },
        { metric: `RMSE vs Human Avg`, value: model.overall.rmse_llm_vs_score_avg },
      ];
    }
    if (model.overall.mae_nlp_vs_score_me !== undefined) {
      return [
        { metric: `MAE vs Data Scientist`, value: model.overall.mae_nlp_vs_score_me },
        { metric: `RMSE vs Data Scientist`, value: model.overall.rmse_nlp_vs_score_me },
        { metric: `MAE vs Researcher`, value: model.overall.mae_nlp_vs_score_other },
        { metric: `RMSE vs Researcher`, value: model.overall.rmse_nlp_vs_score_other },
        { metric: `MAE vs Human Avg`, value: model.overall.mae_nlp_vs_score_avg },
        { metric: `RMSE vs Human Avg`, value: model.overall.rmse_nlp_vs_score_avg },
      ];
    }
    return [];
  };

  const errorBars = useMemo(() => getErrorData(), [model]);

  // Comparison data across all approaches
  const comparisonData = useMemo(() => {
    const data: Array<{
      approach: string;
      color: string;
      humanAvg: number;
      aiScore: number;
      aiName: string;
      pearson: number;
      mae: number;
      rmse: number;
      bias: number;
    }> = [];
    
    Object.entries(allApproachesData).forEach(([key, approachData]) => {
      if (approachData) {
        const aiScore = approachData.overall.means.llm_score ?? approachData.overall.means.nlp_score ?? 0;
        const aiName = approachData.overall.means.llm_score !== undefined ? "LLM" : "NLP";
        const humanAvg = approachData.overall.means.score_avg ?? 0;
        
        data.push({
          approach: approaches[key as keyof typeof approaches]?.name || key,
          color: approaches[key as keyof typeof approaches]?.color || "#6b7280",
          humanAvg: humanAvg,
          aiScore: aiScore,
          aiName: aiName,
          pearson: approachData.overall.pearson_llm_vs_score_avg ?? approachData.overall.pearson_nlp_vs_score_avg ?? 0,
          mae: approachData.overall.mae_llm_vs_score_avg ?? approachData.overall.mae_nlp_vs_score_avg ?? 0,
          rmse: approachData.overall.rmse_llm_vs_score_avg ?? approachData.overall.rmse_nlp_vs_score_avg ?? 0,
          bias: (aiScore - humanAvg) // Score bias vs human avg
        });
      }
    });
    
    return data;
  }, [allApproachesData]);

  // Average scores comparison
  const averageScoresData = useMemo(() => {
    const humanAvg = comparisonData.length > 0 ? comparisonData[0].humanAvg : 0;
    const aiScores = comparisonData.map(d => ({
      name: d.approach,
      value: d.aiScore,
      color: d.color
    }));
    
    return {
      human: humanAvg,
      ai: aiScores
    };
  }, [comparisonData]);

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
          <div className="flex-1">
            <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">{title}</h1>
            <p className="text-sm text-gray-500 dark:text-gray-400">Comparing different AI grading approaches against human evaluators</p>
            
            {/* Approach Selector */}
            <div className="mt-3 flex flex-wrap gap-2">
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Grading Approach:</label>
              <select
                value={selectedApproach}
                onChange={(e) => setSelectedApproach(e.target.value)}
                className="rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 px-3 py-1 text-sm focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400 focus:border-transparent transition-colors"
              >
                {Object.entries(approaches).map(([key, approach]) => (
                  <option key={key} value={key}>{approach.name}</option>
                ))}
              </select>
              <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                {approaches[selectedApproach as keyof typeof approaches]?.description}
              </div>
            </div>
          </div>
          
          <button
            onClick={toggleDarkMode}
            className="p-2 rounded-lg bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors ml-4"
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
          <StatCard label="Human Average" value={fmt(model.overall.means.score_avg)} hint={`Data Scientist: ${fmt(model.overall.means.score_me)} · Researcher: ${fmt(model.overall.means.score_other)}`} />
          <StatCard label={getAIScoreName()} value={fmt(getAIScore())} hint={`Current approach: ${approaches[selectedApproach as keyof typeof approaches]?.name}`} />
        </div>

        {/* Charts */}
        <div className="space-y-6">
          {/* Average Scores Comparison */}
          <Section title="Average Scores Comparison">
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={averageScoresData.ai}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis domain={[0, 5]} />
                  <Tooltip formatter={(value) => [fmt(Number(value)), 'Score']} />
                  <Bar dataKey="value" fill="#3b82f6" />
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div className="text-xs text-gray-500 dark:text-gray-400 mt-2">
              <strong>Explanation:</strong> Compares average AI scores across different grading approaches. Human average: {fmt(averageScoresData.human)}. Higher scores indicate more lenient grading.
            </div>
          </Section>

          {/* Line Charts for Metrics Comparison */}
          <div className="grid lg:grid-cols-2 gap-6">
            {/* Pearson Correlation */}
            <Section title="Pearson Correlation Comparison">
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={comparisonData} margin={{ top: 5, right: 30, left: 20, bottom: 60 }}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis 
                      dataKey="approach" 
                      angle={-45}
                      textAnchor="end"
                      height={80}
                      interval={0}
                      fontSize={12}
                    />
                    <YAxis domain={[0, 1]} />
                    <Tooltip formatter={(value) => [fmt(Number(value)), 'Correlation']} />
                    <Line type="monotone" dataKey="pearson" stroke="#10b981" strokeWidth={3} dot={{ fill: '#10b981', strokeWidth: 2, r: 6 }} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
              <div className="text-xs text-gray-500 dark:text-gray-400 mt-2">
                <strong>Explanation:</strong> Pearson correlation (0-1) measures linear relationship between AI and human scores. <strong>Higher values (closer to 1) are better</strong> - they indicate AI scores align well with human judgment patterns.
              </div>
            </Section>

            {/* MAE Comparison */}
            <Section title="Mean Absolute Error (MAE) Comparison">
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={comparisonData} margin={{ top: 5, right: 30, left: 20, bottom: 60 }}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis 
                      dataKey="approach" 
                      angle={-45}
                      textAnchor="end"
                      height={80}
                      interval={0}
                      fontSize={12}
                    />
                    <YAxis domain={[0, 2]} />
                    <Tooltip formatter={(value) => [fmt(Number(value)), 'MAE']} />
                    <Line type="monotone" dataKey="mae" stroke="#ef4444" strokeWidth={3} dot={{ fill: '#ef4444', strokeWidth: 2, r: 6 }} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
              <div className="text-xs text-gray-500 dark:text-gray-400 mt-2">
                <strong>Explanation:</strong> MAE measures average absolute difference between AI and human scores. <strong>Lower values are better</strong> - they indicate AI predictions are closer to human scores on average.
              </div>
            </Section>

            {/* RMSE Comparison */}
            <Section title="Root Mean Square Error (RMSE) Comparison">
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={comparisonData} margin={{ top: 5, right: 30, left: 20, bottom: 60 }}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis 
                      dataKey="approach" 
                      angle={-45}
                      textAnchor="end"
                      height={80}
                      interval={0}
                      fontSize={12}
                    />
                    <YAxis domain={[0, 2]} />
                    <Tooltip formatter={(value) => [fmt(Number(value)), 'RMSE']} />
                    <Line type="monotone" dataKey="rmse" stroke="#8b5cf6" strokeWidth={3} dot={{ fill: '#8b5cf6', strokeWidth: 2, r: 6 }} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
              <div className="text-xs text-gray-500 dark:text-gray-400 mt-2">
                <strong>Explanation:</strong> RMSE penalizes larger errors more heavily than MAE. <strong>Lower values are better</strong> - they indicate AI predictions have fewer large deviations from human scores.
              </div>
            </Section>

            {/* Score Bias Comparison */}
            <Section title="Score Bias vs Human Average">
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={comparisonData} margin={{ top: 5, right: 30, left: 20, bottom: 60 }}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis 
                      dataKey="approach" 
                      angle={-45}
                      textAnchor="end"
                      height={80}
                      interval={0}
                      fontSize={12}
                    />
                    <YAxis domain={[-1, 1]} />
                    <Tooltip formatter={(value) => [fmt(Number(value)), 'Bias']} />
                    <Line type="monotone" dataKey="bias" stroke="#f59e0b" strokeWidth={3} dot={{ fill: '#f59e0b', strokeWidth: 2, r: 6 }} />
                    <Line type="monotone" dataKey="zero" stroke="#6b7280" strokeDasharray="5 5" strokeWidth={1} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
              <div className="text-xs text-gray-500 dark:text-gray-400 mt-2">
                <strong>Explanation:</strong> Score bias shows how much AI scores differ from human average. <strong>Values closer to 0 are better</strong> - positive values indicate AI is more lenient, negative values indicate AI is harsher than humans.
              </div>
            </Section>
          </div>
        </div>

        {/* Reference Similarity */}
        <Section title="Reference Similarity (Desired Answer vs LLM References)">
          <div className="grid md:grid-cols-5 gap-4">
            <StatCard 
              label="Avg Jaccard" 
              value={fmt(model.overall.reference_similarity?.desired_vs_llm_avg_jaccard_mean)} 
              hint="Average similarity between desired and LLM answers"
            />
            <StatCard 
              label="Max Jaccard" 
              value={fmt(model.overall.reference_similarity?.desired_vs_llm_max_jaccard_mean)} 
              hint="Highest similarity between desired and any LLM answer"
            />
            <StatCard 
              label="LLM Ref Diversity" 
              value={fmt(model.overall.reference_similarity?.llm_answer_pairwise_avg_jaccard_mean)} 
              hint="How similar LLM answers are to each other"
            />
            <StatCard 
              label="Desired Len (tokens)" 
              value={fmt(model.overall.reference_similarity?.desired_len_tokens_mean, 1)} 
              hint="Average length of desired answers"
            />
            <StatCard 
              label="LLM Ref Len (tokens)" 
              value={fmt(model.overall.reference_similarity?.llm_len_tokens_avg_mean, 1)} 
              hint="Average length of LLM-generated answers"
            />
          </div>
          <div className="mt-4 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
            <h4 className="font-semibold text-blue-800 dark:text-blue-200 mb-2">Jaccard Similarity Explained:</h4>
            <div className="text-sm text-blue-700 dark:text-blue-300 space-y-2">
              <p><strong>Jaccard Similarity (0-1):</strong> Measures how similar two text answers are by comparing the overlap of their words/tokens.</p>
              <p><strong>Avg Jaccard:</strong> Average similarity between the desired answer and all LLM-generated answers. <strong>Higher values (closer to 1) are better</strong> - they indicate LLM answers are more similar to the expected answer.</p>
              <p><strong>Max Jaccard:</strong> The highest similarity found between the desired answer and any single LLM answer. Shows the best-case scenario for answer quality.</p>
              <p><strong>LLM Ref Diversity:</strong> How similar the LLM-generated answers are to each other. <strong>Lower values indicate more diversity</strong> - LLM is generating varied answers rather than repetitive ones.</p>
            </div>
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
                <option value="llm_score">Mean AI Score</option>
                <option value="score_avg">Mean Human Avg</option>
                <option value="pearson_llm_vs_score_avg">Correlation (AI vs Human Avg)</option>
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
                  <th className="py-2 pr-4">AI Avg</th>
                  <th className="py-2 pr-4">Corr (AI vs Human Avg)</th>
                  <th className="py-2 pr-4">MAE (vs Human Avg)</th>
                  <th className="py-2 pr-4">AI Min–Max</th>
                </tr>
              </thead>
              <tbody>
                {filteredQuestions.map((q) => {
                  const ag = q.scores.agreement_and_errors;
                  const aiScore = q.scores.means.llm_score ?? q.scores.means.nlp_score ?? 0;
                  const aiMin = q.scores.llm_min ?? q.scores.nlp_min ?? 0;
                  const aiMax = q.scores.llm_max ?? q.scores.nlp_max ?? 0;
                  const correlation = ag.pearson_llm_vs_score_avg ?? ag.pearson_nlp_vs_score_avg ?? 0;
                  const mae = ag.mae_llm_vs_score_avg ?? ag.mae_nlp_vs_score_avg ?? 0;
                  const quantiles = q.scores.llm_quantiles || q.scores.nlp_quantiles || {};
                  
                  return (
                    <tr key={q.question_id} className="border-t border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors">
                      <td className="py-2 pr-4 font-mono text-gray-900 dark:text-gray-100">{q.question_id}</td>
                      <td className="py-2 pr-4 max-w-3xl">
                        <div className="font-medium text-gray-900 dark:text-gray-100">{q.question}</div>
                        <div className="text-xs text-gray-500 dark:text-gray-400">Max {q.max_point ?? "–"} · Quantiles: {Object.entries(quantiles).map(([k,v]) => `${k}:${fmt(v,1)}`).join(" · ")}</div>
                      </td>
                      <td className="py-2 pr-4 text-gray-900 dark:text-gray-100">{q.counts.answers_n}</td>
                      <td className="py-2 pr-4 text-gray-900 dark:text-gray-100">{q.counts.dropped_failures ?? 0}</td>
                      <td className="py-2 pr-4 text-gray-900 dark:text-gray-100">{fmt(q.scores.means.score_avg)}</td>
                      <td className="py-2 pr-4 text-gray-900 dark:text-gray-100">{fmt(aiScore)}</td>
                      <td className="py-2 pr-4 text-gray-900 dark:text-gray-100">{fmt(correlation)}</td>
                      <td className="py-2 pr-4 text-gray-900 dark:text-gray-100">{fmt(mae)}</td>
                      <td className="py-2 pr-4 text-gray-900 dark:text-gray-100">{fmt(aiMin)}–{fmt(aiMax)}</td>
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
