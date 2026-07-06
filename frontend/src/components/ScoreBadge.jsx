export default function ScoreBadge({ score }) {
  const level = score >= 70 ? "high" : score >= 40 ? "medium" : "low";
  return <span className={`score score-${level}`}>{score}</span>;
}
