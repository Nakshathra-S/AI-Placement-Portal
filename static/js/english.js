// English Communication & Grammar Checker Client Logic
document.addEventListener('DOMContentLoaded', () => {
  const englishTextInput = document.getElementById('englishTextInput');
  const englishWordCount = document.getElementById('englishWordCount');
  const analyzeEnglishBtn = document.getElementById('analyzeEnglishBtn');

  // Evaluation panel elements matching Screenshot 4
  const englishPlaceholder = document.getElementById('englishPlaceholder');
  const englishResultsContent = document.getElementById('englishResultsContent');
  const englishScoreVal = document.getElementById('englishScoreVal');
  const englishStatusBadge = document.getElementById('englishStatusBadge');
  const englishProgressFill = document.getElementById('englishProgressFill');
  const englishReadinessPercent = document.getElementById('englishReadinessPercent');

  const scoreClarityVal = document.getElementById('scoreClarityVal');
  const scoreGrammarVal = document.getElementById('scoreGrammarVal');
  const scoreStructureVal = document.getElementById('scoreStructureVal');
  const scoreToneVal = document.getElementById('scoreToneVal');
  const scoreVocabVal = document.getElementById('scoreVocabVal');

  const correctionsContainer = document.getElementById('correctionsContainer');
  const correctionsList = document.getElementById('correctionsList');
  const correctedParagraphText = document.getElementById('correctedParagraphText');
  const englishFeedbackText = document.getElementById('englishFeedbackText');

  // Word counter
  function updateWordCount() {
    const text = englishTextInput.value.trim();
    const count = text ? text.split(/\s+/).length : 0;
    englishWordCount.textContent = `${count} words`;
    if (count > 0) {
      englishWordCount.classList.add('highlight');
    } else {
      englishWordCount.classList.remove('highlight');
    }
  }

  englishTextInput.addEventListener('input', updateWordCount);

  // Analyze English Text
  analyzeEnglishBtn.addEventListener('click', async () => {
    const text = englishTextInput.value.trim();
    if (!text) {
      alert('Please enter a paragraph to analyze.');
      englishTextInput.focus();
      return;
    }

    const origText = analyzeEnglishBtn.innerHTML;
    analyzeEnglishBtn.disabled = true;
    analyzeEnglishBtn.innerHTML = '<span class="spinner"></span> Analyzing English...';

    try {
      const res = await fetch('/english/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text })
      });

      const data = await res.json();
      if (res.ok && data.success) {
        renderEnglishAnalysis(data);
      } else {
        alert(data.message || 'English analysis failed.');
      }
    } catch (err) {
      console.error(err);
      alert('Network error while analyzing text.');
    } finally {
      analyzeEnglishBtn.disabled = false;
      analyzeEnglishBtn.innerHTML = origText;
    }
  });

  function renderEnglishAnalysis(data) {
    if (englishPlaceholder) englishPlaceholder.style.display = 'none';
    if (englishResultsContent) englishResultsContent.style.display = 'block';

    const score = Math.round(data.score) || 0;
    englishScoreVal.innerHTML = `${score} <span>/ 10</span>`;

    const statusBadge = (data.status_badge || 'GOOD').toUpperCase();
    englishStatusBadge.textContent = statusBadge;

    let badgeClass = 'poor';
    let fillClass = 'red';

    if (statusBadge === 'EXCELLENT') {
      badgeClass = 'excellent';
      fillClass = 'green';
    } else if (statusBadge === 'GOOD') {
      badgeClass = 'good';
      fillClass = 'green';
    } else if (statusBadge === 'FAIR') {
      badgeClass = 'fair';
      fillClass = 'yellow';
    } else {
      badgeClass = 'poor';
      fillClass = 'red';
    }

    englishStatusBadge.className = `badge-status ${badgeClass}`;

    const percent = data.readiness_percentage || (score * 10);
    englishProgressFill.style.width = `${percent}%`;
    englishProgressFill.className = `progress-fill ${fillClass}`;
    englishReadinessPercent.textContent = `${percent}%`;

    // Category breakdown
    const bd = data.score_breakdown || {};
    scoreClarityVal.textContent = `${bd.clarity ?? score}/10`;
    scoreGrammarVal.textContent = `${bd.grammar ?? score}/10`;
    scoreStructureVal.textContent = `${bd.sentence_structure ?? score}/10`;
    scoreToneVal.textContent = `${bd.tone ?? score}/10`;
    scoreVocabVal.textContent = `${bd.vocabulary ?? score}/10`;

    // Render corrections
    const corrections = data.corrections || [];
    if (corrections.length > 0) {
      correctionsContainer.style.display = 'block';
      correctionsList.innerHTML = '';
      corrections.forEach(c => {
        const item = document.createElement('div');
        item.className = 'correction-item';
        item.innerHTML = `
          <span class="correction-original">${escapeHtml(c.original || '')}</span>
          <span class="correction-arrow">→</span>
          <span class="correction-fixed">${escapeHtml(c.corrected || '')}</span>
          <div class="correction-reason">${escapeHtml(c.reason || '')}</div>
        `;
        correctionsList.appendChild(item);
      });
    } else {
      correctionsContainer.style.display = 'none';
    }

    // Polished version
    correctedParagraphText.textContent = data.corrected_text || englishTextInput.value;

    // Feedback & Suggestions
    let fullFeedback = data.feedback || '';
    if (data.suggestions) {
      fullFeedback += '\n\n' + data.suggestions;
    }
    englishFeedbackText.textContent = fullFeedback;

    if (window.innerWidth < 900) {
      englishResultsContent.scrollIntoView({ behavior: 'smooth' });
    }
  }

  function escapeHtml(str) {
    return str.replace(/[&<>'"]/g, 
      tag => ({
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        "'": '&#39;',
        '"': '&quot;'
      }[tag] || tag)
    );
  }

  // Initial word count
  updateWordCount();
});
