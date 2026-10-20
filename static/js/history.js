// History Management JavaScript matching Screenshot 5
document.addEventListener('DOMContentLoaded', () => {
  const historyListContainer = document.getElementById('historyListContainer');
  const historyNotification = document.getElementById('historyNotification');

  function showNotification(msg) {
    if (!historyNotification) return;
    historyNotification.textContent = msg;
    historyNotification.style.display = 'block';
    setTimeout(() => {
      historyNotification.style.display = 'none';
    }, 4000);
  }

  async function loadHistory() {
    try {
      const res = await fetch('/history/data');
      const data = await res.json();

      if (!res.ok || !data.attempts) {
        historyListContainer.innerHTML = `
          <div class="empty-state">
            <p>Failed to load attempt history. Please refresh.</p>
          </div>
        `;
        return;
      }

      const attempts = data.attempts;

      if (attempts.length === 0) {
        historyListContainer.innerHTML = `
          <div class="empty-state">
            <div class="empty-state-icon">📋</div>
            <p>No previous attempts found. Complete any interview practice module to track your diagnostic progress.</p>
          </div>
        `;
        return;
      }

      historyListContainer.innerHTML = '';
      attempts.forEach(attempt => {
        const card = createHistoryCard(attempt);
        historyListContainer.appendChild(card);
      });

    } catch (err) {
      console.error(err);
      historyListContainer.innerHTML = `
        <div class="empty-state">
          <p>Network error loading history. Please check your connection.</p>
        </div>
      `;
    }
  }

  function createHistoryCard(attempt) {
    const card = document.createElement('div');
    card.className = 'history-card';
    card.id = `historyCard-${attempt.module_type}-${attempt.attempt_id}`;

    // Score pill class
    const score = parseFloat(attempt.score) || 0;
    let scoreClass = 'score-red';
    if (score >= 8.0) {
      scoreClass = 'score-green';
    } else if (score >= 5.0) {
      scoreClass = 'score-yellow';
    }

    card.innerHTML = `
      <div class="history-top-row">
        <div class="history-badge-group">
          <span class="history-module-pill">${escapeHtml(attempt.badge_label || 'ASSESSMENT')}</span>
          <span class="history-date">${escapeHtml(attempt.created_at || '')}</span>
        </div>
        <div class="history-right-group">
          <span class="history-score-pill ${scoreClass}">
            ${score % 1 === 0 ? score.toFixed(0) : score.toFixed(1)}/10
          </span>
          <button type="button" class="btn btn-danger btn-delete-attempt" data-mod="${attempt.module_type}" data-id="${attempt.attempt_id}">
            Delete
          </button>
        </div>
      </div>

      <div class="history-title">${escapeHtml(attempt.title || `Attempt Record #${attempt.attempt_id}`)}</div>

      <button type="button" class="history-toggle-link" data-target="report-${attempt.module_type}-${attempt.attempt_id}">
        <span>▶ View AI Diagnostic Report & Score Breakdown</span>
      </button>

      <div class="history-expanded-body" id="report-${attempt.module_type}-${attempt.attempt_id}">
        ${renderReportBody(attempt)}
      </div>
    `;

    // Attach Toggle Listener
    const toggleBtn = card.querySelector('.history-toggle-link');
    const expandedBody = card.querySelector('.history-expanded-body');

    toggleBtn.addEventListener('click', () => {
      const isOpen = expandedBody.classList.toggle('open');
      toggleBtn.innerHTML = isOpen
        ? '<span>▼ Hide AI Diagnostic Report</span>'
        : '<span>▶ View AI Diagnostic Report & Score Breakdown</span>';
    });

    // Attach Delete Listener
    const deleteBtn = card.querySelector('.btn-delete-attempt');
    deleteBtn.addEventListener('click', async () => {
      const confirmDelete = confirm(`Are you sure you want to permanently delete Attempt Record #${attempt.attempt_id}?`);
      if (!confirmDelete) return;

      const origText = deleteBtn.innerHTML;
      deleteBtn.disabled = true;
      deleteBtn.innerHTML = '...';

      try {
        const res = await fetch(`/history/${attempt.module_type}/${attempt.attempt_id}`, {
          method: 'DELETE'
        });
        const resData = await res.json();

        if (res.ok && resData.success) {
          card.remove();
          showNotification(resData.message || `Record #${attempt.attempt_id} deleted successfully.`);
          // If no cards left
          if (historyListContainer.children.length === 0) {
            historyListContainer.innerHTML = `
              <div class="empty-state">
                <div class="empty-state-icon">📋</div>
                <p>No previous attempts remaining.</p>
              </div>
            `;
          }
        } else {
          alert(resData.message || 'Could not delete record.');
          deleteBtn.disabled = false;
          deleteBtn.innerHTML = origText;
        }
      } catch (e) {
        console.error(e);
        alert('Network error deleting record.');
        deleteBtn.disabled = false;
        deleteBtn.innerHTML = origText;
      }
    });

    return card;
  }

  function renderReportBody(attempt) {
    const d = attempt.details || {};
    let content = '';

    if (attempt.module_type === 'technical') {
      content = `
        <div style="margin-bottom: 12px;">
          <strong style="color: var(--text-main);">Question:</strong>
          <p style="color: var(--text-body); font-size: 0.9rem; margin-top: 4px;">${escapeHtml(d.question || '')}</p>
        </div>
        <div style="margin-bottom: 12px;">
          <strong style="color: var(--text-main);">Submitted Answer:</strong>
          <p style="color: var(--text-body); font-size: 0.88rem; background: var(--bg-page); padding: 10px; border-radius: 6px; border: 1px solid var(--border); margin-top: 4px;">
            ${escapeHtml(d.answer || '')}
          </p>
        </div>
        ${d.feedback ? `<div style="margin-bottom: 10px;"><strong>Feedback:</strong> <span style="color: var(--text-body);">${escapeHtml(d.feedback)}</span></div>` : ''}
        ${d.model_answer ? `<div style="margin-bottom: 10px;"><strong>Model Answer:</strong> <p style="color: var(--primary); font-size: 0.88rem; margin-top: 4px;">${escapeHtml(d.model_answer)}</p></div>` : ''}
      `;
    } else if (attempt.module_type === 'hr') {
      content = `
        <div style="margin-bottom: 12px;">
          <strong style="color: var(--text-main);">HR Question:</strong>
          <p style="color: var(--text-body); font-size: 0.9rem; margin-top: 4px;">${escapeHtml(d.question || '')}</p>
        </div>
        <div style="margin-bottom: 12px;">
          <strong style="color: var(--text-main);">Your Answer:</strong>
          <p style="color: var(--text-body); font-size: 0.88rem; background: var(--bg-page); padding: 10px; border-radius: 6px; border: 1px solid var(--border); margin-top: 4px;">
            ${escapeHtml(d.answer || '')}
          </p>
        </div>
        ${d.feedback ? `<div style="margin-bottom: 10px;"><strong>HR Assessment:</strong> <span style="color: var(--text-body);">${escapeHtml(d.feedback)}</span></div>` : ''}
        ${d.model_answer ? `<div style="margin-bottom: 10px;"><strong>Exemplary Response:</strong> <p style="color: var(--primary); font-size: 0.88rem; margin-top: 4px;">${escapeHtml(d.model_answer)}</p></div>` : ''}
      `;
    } else if (attempt.module_type === 'gd') {
      content = `
        <div style="margin-bottom: 12px;">
          <strong style="color: var(--text-main);">GD Topic:</strong>
          <p style="color: var(--text-body); font-size: 0.9rem; margin-top: 4px;">${escapeHtml(d.topic || '')}</p>
        </div>
        <div style="margin-bottom: 12px;">
          <strong style="color: var(--text-main);">Submitted Contribution:</strong>
          <p style="color: var(--text-body); font-size: 0.88rem; background: var(--bg-page); padding: 10px; border-radius: 6px; border: 1px solid var(--border); margin-top: 4px;">
            ${escapeHtml(d.opinion || '')}
          </p>
        </div>
        ${d.feedback ? `<div style="margin-bottom: 10px;"><strong>Moderator Feedback:</strong> <span style="color: var(--text-body);">${escapeHtml(d.feedback)}</span></div>` : ''}
        ${d.model_discussion ? `<div style="margin-bottom: 10px;"><strong>Model Discussion Standpoint:</strong> <p style="color: var(--primary); font-size: 0.88rem; margin-top: 4px;">${escapeHtml(d.model_discussion)}</p></div>` : ''}
      `;
    } else if (attempt.module_type === 'english') {
      content = `
        <div style="margin-bottom: 12px;">
          <strong style="color: var(--text-main);">Original Input Text:</strong>
          <p style="color: var(--text-body); font-size: 0.88rem; background: var(--bg-page); padding: 10px; border-radius: 6px; border: 1px solid var(--border); margin-top: 4px;">
            ${escapeHtml(d.input_text || '')}
          </p>
        </div>
        ${d.corrected_text ? `
          <div style="margin-bottom: 12px;">
            <strong style="color: var(--success-text);">Corrected Professional Version:</strong>
            <p style="color: var(--text-body); font-size: 0.88rem; background: var(--success-bg); padding: 10px; border-radius: 6px; margin-top: 4px;">
              ${escapeHtml(d.corrected_text)}
            </p>
          </div>
        ` : ''}
        ${d.feedback ? `<div style="margin-bottom: 10px;"><strong>Linguistic Diagnostic:</strong> <span style="color: var(--text-body);">${escapeHtml(d.feedback)}</span></div>` : ''}
      `;
    }

    return content;
  }

  function escapeHtml(str) {
    if (!str) return '';
    return String(str).replace(/[&<>'"]/g, 
      tag => ({
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        "'": '&#39;',
        '"': '&quot;'
      }[tag] || tag)
    );
  }

  // Initial load
  loadHistory();
});
