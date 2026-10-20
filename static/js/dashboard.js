// Dashboard metrics refresher
document.addEventListener('DOMContentLoaded', () => {
  // Option to periodically refresh or sync stats
  async function refreshStats() {
    try {
      const res = await fetch('/dashboard/stats');
      if (!res.ok) return;
      const data = await res.json();
      
      const totalEl = document.getElementById('statTotal');
      const avgEl = document.getElementById('statAvg');
      const bestEl = document.getElementById('statBest');
      const readEl = document.getElementById('statReadiness');

      if (totalEl) totalEl.textContent = data.total_attempts;
      if (avgEl) avgEl.innerHTML = `${data.average_score}<span>/10</span>`;
      if (bestEl) bestEl.innerHTML = `${data.best_score}<span>/10</span>`;
      if (readEl) {
        const percent = data.total_attempts > 0 ? Math.round(data.average_score * 10) : 0;
        readEl.textContent = `${percent}%`;
      }
    } catch (e) {
      console.debug('Dashboard sync:', e);
    }
  }

  // Initial sync
  refreshStats();
});
