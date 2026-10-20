// HR Behavioral Interview Practice Client Logic
document.addEventListener('DOMContentLoaded', () => {
  const loadHrBtn = document.getElementById('loadHrBtn');
  const hrQuestionsContainer = document.getElementById('hrQuestionsContainer');

  // Evaluation panel elements
  const hrPlaceholder = document.getElementById('hrPlaceholder');
  const hrResultsContent = document.getElementById('hrResultsContent');
  const hrScoreVal = document.getElementById('hrScoreVal');
  const hrScoreBadge = document.getElementById('hrScoreBadge');
  const hrProgressFill = document.getElementById('hrProgressFill');
  const starSituation = document.getElementById('starSituation');
  const starTask = document.getElementById('starTask');
  const starAction = document.getElementById('starAction');
  const starResult = document.getElementById('starResult');
  const starTone = document.getElementById('starTone');
  const hrStrengths = document.getElementById('hrStrengths');
  const hrWeaknesses = document.getElementById('hrWeaknesses');
  const hrModelAnswer = document.getElementById('hrModelAnswer');
  const hrSuggestions = document.getElementById('hrSuggestions');

  function setupQuestionCard(card) {
    const textarea = card.querySelector('.hr-input');
    const wordBadge = card.querySelector('.hr-words');
    const evalBtn = card.querySelector('.btn-eval-hr');
    const qTitle = card.querySelector('.question-text');

    if (!textarea || !wordBadge || !evalBtn) return;

    // Real-time word counter
    textarea.addEventListener('input', () => {
      const text = textarea.value.trim();
      const count = text ? text.split(/\s+/).length : 0;
      wordBadge.textContent = `${count} words`;
      if (count >= 25) {
        wordBadge.classList.add('highlight');
      } else {
        wordBadge.classList.remove('highlight');
      }
    });

    // Evaluate
    evalBtn.addEventListener('click', async () => {
      const answer = textarea.value.trim();
      if (!answer) {
        alert('Please enter your response before submitting.');
        textarea.focus();
        return;
      }

      const origText = evalBtn.innerHTML;
      evalBtn.disabled = true;
      evalBtn.innerHTML = '<span class="spinner"></span> Evaluating...';

      try {
        const res = await fetch('/hr/evaluate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            question_text: qTitle ? qTitle.textContent.trim() : 'HR Behavioral Question',
            submitted_answer: answer
          })
        });

        const data = await res.json();
        if (res.ok && data.success) {
          renderHrEvaluation(data);
        } else {
          alert(data.message || 'HR evaluation failed.');
        }
      } catch (err) {
        console.error(err);
        alert('Network error while evaluating HR response.');
      } finally {
        evalBtn.disabled = false;
        evalBtn.innerHTML = origText;
      }
    });
  }

  // Setup initial cards
  document.querySelectorAll('.hr-question-card').forEach(setupQuestionCard);

  // Load All HR Questions Button
  if (loadHrBtn) {
    loadHrBtn.addEventListener('click', async () => {
      const orig = loadHrBtn.innerHTML;
      loadHrBtn.disabled = true;
      loadHrBtn.innerHTML = '<span class="spinner"></span> Loading Questions...';

      try {
        const res = await fetch('/hr/questions');
        const data = await res.json();

        if (res.ok && data.questions) {
          hrQuestionsContainer.innerHTML = '';
          data.questions.forEach((q) => {
            const card = document.createElement('div');
            card.className = 'content-card hr-question-card';
            card.dataset.qid = q.id;
            card.innerHTML = `
              <div class="card-header-row" style="margin-bottom: 8px;">
                <h3 class="question-text" style="margin-bottom: 0;">${q.question}</h3>
                <span class="word-count-badge hr-words">0 words</span>
              </div>
              <div class="form-group" style="margin-bottom: 12px;">
                <textarea 
                  class="form-textarea hr-input" 
                  placeholder="${q.placeholder}"
                  rows="5"
                ></textarea>
              </div>
              <div class="card-footer-row" style="margin-top: 0;">
                <span class="footer-caption">Behavioral rubric active</span>
                <button type="button" class="btn btn-primary btn-eval-hr">
                  <span>Submit & Evaluate →</span>
                </button>
              </div>
            `;
            hrQuestionsContainer.appendChild(card);
            setupQuestionCard(card);
          });
        }
      } catch (err) {
        console.error(err);
        alert('Failed to load HR questions from server.');
      } finally {
        loadHrBtn.disabled = false;
        loadHrBtn.innerHTML = orig;
      }
    });
  }

  function renderHrEvaluation(data) {
    hrPlaceholder.style.display = 'none';
    hrResultsContent.style.display = 'block';

    const score = parseFloat(data.score) || 0;
    hrScoreVal.innerHTML = `${score.toFixed(1)}<span>/ 10</span>`;

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

    hrScoreBadge.className = `badge-status ${badgeClass}`;
    hrScoreBadge.textContent = badgeLabel;

    const percent = Math.min(100, Math.round(score * 10));
    hrProgressFill.style.width = `${percent}%`;
    hrProgressFill.className = `progress-fill ${fillClass}`;

    const bd = data.score_breakdown || {};
    starSituation.textContent = `${bd.situation ?? '-'}/10`;
    starTask.textContent = `${bd.task ?? '-'}/10`;
    starAction.textContent = `${bd.action ?? '-'}/10`;
    starResult.textContent = `${bd.result ?? '-'}/10`;
    starTone.textContent = `${bd.professionalism ?? '-'}/10`;

    hrStrengths.textContent = data.strengths || 'Professional demeanor and clear structure.';
    hrWeaknesses.textContent = data.weaknesses || 'Needs more specific personal contributions and measurable results.';
    hrModelAnswer.textContent = data.model_answer || 'Provide a crisp STAR story.';
    hrSuggestions.textContent = data.suggestions || 'Quantify results using metrics and articulate clear leadership traits.';

    if (window.innerWidth < 900) {
      hrResultsContent.scrollIntoView({ behavior: 'smooth' });
    }
  }
});
