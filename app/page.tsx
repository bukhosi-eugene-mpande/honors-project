import GradingDashboard from "@/app/components/GradingDashboard";

export default function Home() {
  return <GradingDashboard dataUrl="/graded_stats.json" />;
}
