// Technical Interview Practice Client Logic
document.addEventListener('DOMContentLoaded', () => {
  const jobRoleSelect = document.getElementById('jobRoleSelect');
  const generateQuestionsBtn = document.getElementById('generateQuestionsBtn');
  const technicalAnswerInput = document.getElementById('technicalAnswerInput');
  const wordCountBadge = document.getElementById('wordCountBadge');
  const submitAnswerBtn = document.getElementById('submitAnswerBtn');
  const questionDisplay = document.getElementById('questionDisplay');
  const questionProgressTag = document.getElementById('questionProgressTag');
  const navQuestionsRow = document.getElementById('navQuestionsRow');
  const prevQBtn = document.getElementById('prevQBtn');
  const nextQBtn = document.getElementById('nextQBtn');
  const qIndicatorText = document.getElementById('qIndicatorText');

  // Evaluation panel elements
  const evalPlaceholder = document.getElementById('evalPlaceholder');
  const evalResultsContent = document.getElementById('evalResultsContent');
  const techScoreVal = document.getElementById('techScoreVal');
  const techScoreBadge = document.getElementById('techScoreBadge');
  const techProgressFill = document.getElementById('techProgressFill');
  const scoreConcept = document.getElementById('scoreConcept');
  const scoreFactual = document.getElementById('scoreFactual');
  const scoreComplete = document.getElementById('scoreComplete');
  const scoreClarity = document.getElementById('scoreClarity');
  const techStrengths = document.getElementById('techStrengths');
  const techMissing = document.getElementById('techMissing');
  const techModelAnswer = document.getElementById('techModelAnswer');
  const techSuggestions = document.getElementById('techSuggestions');

  let currentQuestions = [
    "As a Full Stack Developer, you often work with both frontend and backend technologies. Can you explain the differences between client-side rendering (CSR) and server-side rendering (SSR) and when you might choose one over the other for a web application?"
  ];
  let currentQuestionIndex = 0;
  let userAnswers = {};

  // Word Counter
  function updateWordCount() {
    const text = technicalAnswerInput.value.trim();
    const words = text ? text.split(/\s+/).length : 0;
    wordCountBadge.textContent = `${words} words`;
    if (words >= 20) {
      wordCountBadge.classList.add('highlight');
    } else {
      wordCountBadge.classList.remove('highlight');
    }
  }

  technicalAnswerInput.addEventListener('input', updateWordCount);

  // Generate Questions via Backend
  generateQuestionsBtn.addEventListener('click', async () => {
    const selectedRole = jobRoleSelect.value;
    const originalText = generateQuestionsBtn.innerHTML;
    generateQuestionsBtn.disabled = true;
    generateQuestionsBtn.innerHTML = '<span class="spinner"></span> Generating Questions...';

    try {
      const res = await fetch('/technical/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ job_role: selectedRole })
      });

      const data = await res.json();
      if (res.ok && data.questions && data.questions.length > 0) {
        currentQuestions = data.questions;
        currentQuestionIndex = 0;
        userAnswers = {};
        loadQuestion(0);
        navQuestionsRow.style.display = 'flex';
      } else {
        alert(data.message || 'Failed to generate questions. Please try again.');
      }
    } catch (err) {
      console.error(err);
      alert('Error connecting to backend server.');
    } finally {
      generateQuestionsBtn.disabled = false;
      generateQuestionsBtn.innerHTML = originalText;
    }
  });

  function loadQuestion(index) {
    if (index < 0 || index >= currentQuestions.length) return;
    currentQuestionIndex = index;

    questionProgressTag.textContent = `QUESTION ${index + 1} OF ${currentQuestions.length}`;
    questionDisplay.textContent = currentQuestions[index];
    qIndicatorText.textContent = `Question ${index + 1} of ${currentQuestions.length}`;

    // Restore previously typed answer if any
    technicalAnswerInput.value = userAnswers[index] || '';
    updateWordCount();

    // Update navigation button states
    prevQBtn.disabled = (index === 0);
    nextQBtn.disabled = (index === currentQuestions.length - 1);
  }

  prevQBtn.addEventListener('click', () => {
    userAnswers[currentQuestionIndex] = technicalAnswerInput.value;
    loadQuestion(currentQuestionIndex - 1);
  });

  nextQBtn.addEventListener('click', () => {
    userAnswers[currentQuestionIndex] = technicalAnswerInput.value;
    loadQuestion(currentQuestionIndex + 1);
  });

  // Submit and Evaluate Answer
  submitAnswerBtn.addEventListener('click', async () => {
    const answer = technicalAnswerInput.value.trim();
    if (!answer) {
      alert('Please enter your answer before submitting for evaluation.');
      technicalAnswerInput.focus();
      return;
    }

    const originalBtn = submitAnswerBtn.innerHTML;
    submitAnswerBtn.disabled = true;
    submitAnswerBtn.innerHTML = '<span class="spinner"></span> Strictly Evaluating...';

    const payload = {
      job_role: jobRoleSelect.value,
      question_number: currentQuestionIndex + 1,
      question_text: currentQuestions[currentQuestionIndex],
      submitted_answer: answer
    };

    try {
      const res = await fetch('/technical/evaluate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      const data = await res.json();
      if (res.ok && data.success) {
        renderEvaluation(data);
      } else {
        alert(data.message || 'Evaluation failed. Please try again.');
      }
    } catch (err) {
      console.error(err);
      alert('Network error while evaluating answer.');
    } finally {
      submitAnswerBtn.disabled = false;
      submitAnswerBtn.innerHTML = originalBtn;
    }
  });

  function renderEvaluation(data) {
    evalPlaceholder.style.display = 'none';
    evalResultsContent.style.display = 'block';

    const score = parseFloat(data.score) || 0;
    techScoreVal.innerHTML = `${score.toFixed(1)}<span>/ 10</span>`;

    // Status Badge & Color
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

    techScoreBadge.className = `badge-status ${badgeClass}`;
    techScoreBadge.textContent = badgeLabel;

    const percent = Math.min(100, Math.round(score * 10));
    techProgressFill.style.width = `${percent}%`;
    techProgressFill.className = `progress-fill ${fillClass}`;

    // Breakdown
    const bd = data.score_breakdown || {};
    scoreConcept.textContent = `${bd.conceptual_accuracy ?? '-'}/10`;
    scoreFactual.textContent = `${bd.factual_correctness ?? '-'}/10`;
    scoreComplete.textContent = `${bd.completeness ?? '-'}/10`;
    scoreClarity.textContent = `${bd.clarity ?? '-'}/10`;

    techStrengths.textContent = data.strengths || 'Reasonable attempt at addressing the core prompt.';
    techMissing.textContent = data.missing_concepts || 'Lack of in-depth boundary conditions and production tradeoffs.';
    techModelAnswer.textContent = data.model_answer || 'Refer to engineering documentation.';
    techSuggestions.textContent = data.suggestions || 'Structure your responses using clear architectural bullet points.';

    // Scroll to results on mobile
    if (window.innerWidth < 900) {
      evalResultsContent.scrollIntoView({ behavior: 'smooth' });
    }
  }

  // Initial word count
  updateWordCount();
});
