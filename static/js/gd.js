// Group Discussion Practice Client Logic
document.addEventListener('DOMContentLoaded', () => {
  const generateGdTopicBtn = document.getElementById('generateGdTopicBtn');
  const gdCategoryTag = document.getElementById('gdCategoryTag');
  const gdTopicTitle = document.getElementById('gdTopicTitle');
  const gdContextText = document.getElementById('gdContextText');
  const gdOpinionInput = document.getElementById('gdOpinionInput');
  const gdWordCount = document.getElementById('gdWordCount');
  const submitGdBtn = document.getElementById('submitGdBtn');

  // Evaluation panel elements
  const gdPlaceholder = document.getElementById('gdPlaceholder');
  const gdResultsContent = document.getElementById('gdResultsContent');
  const gdScoreVal = document.getElementById('gdScoreVal');
  const gdScoreBadge = document.getElementById('gdScoreBadge');
  const gdProgressFill = document.getElementById('gdProgressFill');
  const gdRelevance = document.getElementById('gdRelevance');
  const gdArgument = document.getElementById('gdArgument');
  const gdStructure = document.getElementById('gdStructure');
  const gdExamples = document.getElementById('gdExamples');
  const gdComm = document.getElementById('gdComm');
  const gdStrengths = document.getElementById('gdStrengths');
  const gdWeaknesses = document.getElementById('gdWeaknesses');
  const gdCounter = document.getElementById('gdCounter');
  const gdModelText = document.getElementById('gdModelText');

  // Word count tracker
  function updateWordCount() {
    const text = gdOpinionInput.value.trim();
    const count = text ? text.split(/\s+/).length : 0;
    gdWordCount.textContent = `${count} words`;
    if (count >= 30) {
      gdWordCount.classList.add('highlight');
    } else {
      gdWordCount.classList.remove('highlight');
    }
  }

  gdOpinionInput.addEventListener('input', updateWordCount);

  // Generate new topic
  generateGdTopicBtn.addEventListener('click', async () => {
    const orig = generateGdTopicBtn.innerHTML;
    generateGdTopicBtn.disabled = true;
    generateGdTopicBtn.innerHTML = '<span class="spinner"></span> Generating Topic...';

    try {
      const res = await fetch('/gd/generate-topic', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      const data = await res.json();

      if (res.ok && data.data) {
        const t = data.data;
        gdCategoryTag.textContent = (t.category || 'CAMPUS PLACEMENT GD').toUpperCase();
        gdTopicTitle.textContent = t.topic;
        gdContextText.textContent = t.context || 'Participate with structured reasoning, real-world examples, and multi-perspective insights.';
        gdOpinionInput.value = '';
        updateWordCount();
      }
    } catch (err) {
      console.error(err);
      alert('Failed to generate GD topic.');
    } finally {
      generateGdTopicBtn.disabled = false;
      generateGdTopicBtn.innerHTML = orig;
    }
  });

  // Submit and Evaluate Discussion
  submitGdBtn.addEventListener('click', async () => {
    const opinion = gdOpinionInput.value.trim();
    if (!opinion) {
      alert('Please write your arguments before submitting for evaluation.');
      gdOpinionInput.focus();
      return;
    }

    const orig = submitGdBtn.innerHTML;
    submitGdBtn.disabled = true;
    submitGdBtn.innerHTML = '<span class="spinner"></span> Evaluating Contribution...';

    try {
      const res = await fetch('/gd/evaluate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          topic: gdTopicTitle.textContent.trim(),
          submitted_opinion: opinion
        })
      });

      const data = await res.json();
      if (res.ok && data.success) {
        renderGdEvaluation(data);
      } else {
        alert(data.message || 'GD evaluation failed.');
      }
    } catch (err) {
      console.error(err);
      alert('Network error while evaluating group discussion.');
    } finally {
      submitGdBtn.disabled = false;
      submitGdBtn.innerHTML = orig;
    }
  });

  function renderGdEvaluation(data) {
    gdPlaceholder.style.display = 'none';
    gdResultsContent.style.display = 'block';

    const score = parseFloat(data.score) || 0;
    gdScoreVal.innerHTML = `${score.toFixed(1)}<span>/ 10</span>`;

    let badgeClass = 'poor';
    let badgeLabel = 'POOR';
    let fillClass = 'red';

    if (score >= 8.0) {
      badgeClass = 'excellent';
      badgeLabel = 'EXCELLENT';
      fillClass = 'green';
    } else if (score >= 6.5) {
      badgeClass = 'good';
      badgeLabel = 'GOOD';
      fillClass = 'green';
    } else if (score >= 5.0) {
      badgeClass = 'fair';
      badgeLabel = 'FAIR';
      fillClass = 'yellow';
    }

    gdScoreBadge.className = `badge-status ${badgeClass}`;
    gdScoreBadge.textContent = badgeLabel;

    const percent = Math.min(100, Math.round(score * 10));
    gdProgressFill.style.width = `${percent}%`;
    gdProgressFill.className = `progress-fill ${fillClass}`;

    const bd = data.score_breakdown || {};
    gdRelevance.textContent = `${bd.relevance ?? '-'}/10`;
    gdArgument.textContent = `${bd.argument_quality ?? '-'}/10`;
    gdStructure.textContent = `${bd.logical_structure ?? '-'}/10`;
    gdExamples.textContent = `${bd.supporting_examples ?? '-'}/10`;
    gdComm.textContent = `${bd.communication ?? '-'}/10`;

    gdStrengths.textContent = data.strengths || 'Articulated key viewpoints clearly.';
    gdWeaknesses.textContent = data.weaknesses || 'Lacks tangible metrics or real-world empirical examples.';
    gdCounter.textContent = data.counterarguments || 'Could strengthen synthesis by addressing the alternative perspective.';
    gdModelText.textContent = data.model_discussion || 'A balanced argument acknowledging both benefits and challenges.';

    if (window.innerWidth < 900) {
      gdResultsContent.scrollIntoView({ behavior: 'smooth' });
    }
  }

  // Initial count
  updateWordCount();
});
