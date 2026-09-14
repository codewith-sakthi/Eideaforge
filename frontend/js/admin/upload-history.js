/**
 * admin/upload-history.js – View past bulk student uploads and download credentials sheets
 */

document.addEventListener('DOMContentLoaded', async () => {
  if (!auth.requireAuth('admin')) return;

  const historyTbody = document.getElementById('history-tbody');
  const searchInput = document.getElementById('history-search-input');
  const btnRefresh = document.getElementById('btn-refresh-history');

  const statBatches = document.getElementById('stat-total-batches');
  const statStudents = document.getElementById('stat-total-students');
  const statLatestDate = document.getElementById('stat-latest-date');

  const previewModal = document.getElementById('preview-modal');
  const btnCloseModal = document.getElementById('btn-close-modal');
  const modalBtnClose = document.getElementById('modal-btn-close');
  const modalTbody = document.getElementById('modal-tbody');
  const modalBatchName = document.getElementById('modal-batch-name');
  const modalBtnDownload = document.getElementById('modal-btn-download');

  let allHistory = [];
  let currentViewingBatch = null;

  async function loadHistory() {
    try {
      historyTbody.innerHTML = `
        <tr>
          <td colspan="5" style="text-align:center; padding:2rem; color:var(--text-muted);">
            Loading bulk upload history...
          </td>
        </tr>
      `;

      const res = await api.get('/admin/bulk-upload/history');
      allHistory = res.data || [];

      // Update statistics
      statBatches.textContent = allHistory.length;
      const totalStudents = allHistory.reduce((acc, curr) => acc + (curr.student_count || 0), 0);
      statStudents.textContent = totalStudents;
      statLatestDate.textContent = allHistory.length > 0 ? allHistory[0].uploaded_at : 'None';

      renderTable(allHistory);
    } catch (err) {
      console.error('Failed to load history:', err);
      historyTbody.innerHTML = `
        <tr>
          <td colspan="5" style="text-align:center; padding:2rem; color:#dc2626;">
            ❌ Failed to load history: ${utils.escapeHtml(err.message || 'Server error')}
          </td>
        </tr>
      `;
    }
  }

  function renderTable(list) {
    if (!list || list.length === 0) {
      historyTbody.innerHTML = `
        <tr>
          <td colspan="5" style="text-align:center; padding:2.5rem; color:var(--text-muted);">
            <div style="font-size:2rem; margin-bottom:0.5rem;">📂</div>
            <p style="margin:0; font-weight:600;">No bulk upload batches recorded yet.</p>
            <p style="font-size:0.85rem; margin-top:0.25rem;">Upload student CSV files from the CSV Bulk Upload page.</p>
          </td>
        </tr>
      `;
      return;
    }

    historyTbody.innerHTML = list.map(item => `
      <tr>
        <td>
          <div style="display:flex; align-items:center; gap:0.5rem;">
            <span style="font-size:1.2rem;">📊</span>
            <div>
              <div style="font-weight:700; color:var(--text-main); font-size:0.9rem;">${utils.escapeHtml(item.filename)}</div>
              <div style="font-size:0.75rem; color:var(--text-muted);">CSV Log Batch</div>
            </div>
          </div>
        </td>
        <td style="color:var(--text-muted); font-size:0.88rem;">${utils.escapeHtml(item.uploaded_at)}</td>
        <td>
          <span class="status-pill status-approved" style="font-weight:700; font-size:0.8rem; padding:0.25rem 0.65rem;">
            ${item.student_count} Students
          </span>
        </td>
        <td style="color:var(--text-muted); font-size:0.85rem;">${utils.escapeHtml(item.file_size)}</td>
        <td style="text-align:right;">
          <div style="display:inline-flex; gap:0.5rem; align-items:center;">
            <button class="btn btn-outline btn-sm btn-preview" data-filename="${utils.escapeHtml(item.filename)}" style="display:flex; align-items:center; gap:0.3rem; padding:0.35rem 0.75rem; font-size:0.8rem;">
              👁️ Preview
            </button>
            <button class="btn btn-primary btn-sm btn-download" data-filename="${utils.escapeHtml(item.filename)}" style="display:flex; align-items:center; gap:0.3rem; padding:0.35rem 0.75rem; font-size:0.8rem;">
              📥 Download
            </button>
          </div>
        </td>
      </tr>
    `).join('');

    // Attach click handlers
    document.querySelectorAll('.btn-download').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const fname = e.currentTarget.dataset.filename;
        downloadFile(fname);
      });
    });

    document.querySelectorAll('.btn-preview').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const fname = e.currentTarget.dataset.filename;
        const batch = allHistory.find(b => b.filename === fname);
        if (batch) openPreviewModal(batch);
      });
    });
  }

  async function downloadFile(filename) {
    try {
      const token = localStorage.getItem('token');
      const res = await fetch(`/api/admin/bulk-upload/download/${filename}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!res.ok) {
        throw new Error(`Failed to download (Status ${res.status})`);
      }

      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
      utils.showToast(`Downloaded ${filename}`, 'success');
    } catch (err) {
      utils.showToast(err.message || 'Download failed', 'error');
    }
  }

  function openPreviewModal(batch) {
    currentViewingBatch = batch;
    modalBatchName.textContent = `Batch: ${batch.filename} • Logged on ${batch.uploaded_at}`;

    const records = batch.records || [];
    if (records.length === 0) {
      modalTbody.innerHTML = `
        <tr>
          <td colspan="6" style="text-align:center; padding:1.5rem; color:var(--text-muted);">
            No individual records available in this batch.
          </td>
        </tr>
      `;
    } else {
      modalTbody.innerHTML = records.map(r => `
        <tr>
          <td style="font-weight:600; color:var(--text-main);">${utils.escapeHtml(r.name || 'N/A')}</td>
          <td><code>${utils.escapeHtml(r.email || 'N/A')}</code></td>
          <td><code>${utils.escapeHtml(r.roll_number || 'N/A')}</code></td>
          <td>${utils.escapeHtml(r.department || 'N/A')}</td>
          <td><span style="font-family:monospace; background:#fff7ed; padding:0.2rem 0.45rem; border-radius:4px; font-weight:700; color:#ea580c;">${utils.escapeHtml(r.temp_password || '')}</span></td>
          <td style="text-align:center;">
            <button class="btn btn-outline btn-sm" onclick="navigator.clipboard.writeText('${utils.escapeHtml(r.temp_password || '')}').then(() => utils.showToast('Password copied!', 'success'))" style="padding:0.2rem 0.5rem; font-size:0.75rem;">
              📋
            </button>
          </td>
        </tr>
      `).join('');
    }

    previewModal.style.display = 'flex';
  }

  function closeModal() {
    previewModal.style.display = 'none';
    currentViewingBatch = null;
  }

  if (btnCloseModal) btnCloseModal.addEventListener('click', closeModal);
  if (modalBtnClose) modalBtnClose.addEventListener('click', closeModal);
  if (previewModal) {
    previewModal.addEventListener('click', (e) => {
      if (e.target === previewModal) closeModal();
    });
  }

  if (modalBtnDownload) {
    modalBtnDownload.addEventListener('click', () => {
      if (currentViewingBatch) {
        downloadFile(currentViewingBatch.filename);
      }
    });
  }

  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      const q = e.target.value.toLowerCase().trim();
      if (!q) {
        renderTable(allHistory);
        return;
      }
      const filtered = allHistory.filter(item =>
        item.filename.toLowerCase().includes(q) ||
        item.uploaded_at.toLowerCase().includes(q) ||
        (item.records && item.records.some(r =>
          (r.name && r.name.toLowerCase().includes(q)) ||
          (r.email && r.email.toLowerCase().includes(q)) ||
          (r.roll_number && r.roll_number.toLowerCase().includes(q))
        ))
      );
      renderTable(filtered);
    });
  }

  if (btnRefresh) {
    btnRefresh.addEventListener('click', () => {
      loadHistory();
      utils.showToast('History refreshed', 'info');
    });
  }

  await loadHistory();
});
