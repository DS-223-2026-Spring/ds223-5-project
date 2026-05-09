import React from 'react';

export default function ScoreBadge({ score, style }) {
  let cls = 'score-low';
  if (score >= 75) cls = 'score-high';
  else if (score >= 50) cls = 'score-mid';

  return (
    <span className={`score-badge ${cls}`} style={style}>
      {score}%
    </span>
  );
}
