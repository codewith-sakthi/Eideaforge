/**
 * student/idea-form.js – Handler for creating and editing ideas with draft saving and one idea enforcement
 */

document.addEventListener('DOMContentLoaded', async () => {
  if (!auth.requireAuth('student')) return;

  const urlParams = new URLSearchParams(window.location.search);
  const ideaId = urlParams.get('id');
  const isEdit = !!ideaId;

  const form = document.getElementById('idea-form');
  let existingAbstractDocUrl = null;

  // If on create-idea page, check if user already has an idea
  if (!isEdit) {
    try {
      const checkRes = await api.get('/ideas?scope=mine');
      if (checkRes.success && checkRes.data && checkRes.data.length > 0) {
        const existing = checkRes.data[0];
        utils.showToast('You already have an innovation idea created. Redirecting to your idea editor...', 'info');
        setTimeout(() => {
          window.location.href = `/student/edit-idea.html?id=${existing.id}`;
        }, 1200);
        return;
      }
    } catch (e) {
      console.warn('Could not check existing user ideas:', e);
    }
  }

  // If editing, preload data
  if (isEdit) {
    try {
      const res = await api.get(`/ideas/${ideaId}`);
      if (res.success && res.data) {
        const i = res.data;
        document.getElementById('title').value = i.title || '';
        document.getElementById('description').value = i.description || '';
        document.getElementById('problem_statement').value = i.problem_statement || '';
        document.getElementById('solution').value = i.solution || '';
        document.getElementById('category').value = i.category || '';
        document.getElementById('tags').value = i.tags || '';
        
        if (document.getElementById('github_url')) {
          document.getElementById('github_url').value = i.github_url || '';
        }
        if (document.getElementById('drive_url')) {
          document.getElementById('drive_url').value = i.drive_url || '';
        }

        existingAbstractDocUrl = i.abstract_doc_url || null;
        const preview = document.getElementById('current-abstract-preview');
        if (preview && existingAbstractDocUrl) {
          preview.innerHTML = `<a href="${existingAbstractDocUrl}" target="_blank" style="color:var(--primary); font-weight:600; text-decoration:none;">📄 View Uploaded Abstract</a>`;
        }

        updateReadinessScore();
      }
    } catch (err) {
      utils.showToast('Could not load idea data', 'error');
    }
  }

  // Real-time Pitch Readiness Score & Checklist updates
  function updateReadinessScore() {
    const title = (document.getElementById('title') ? document.getElementById('title').value.trim() : '');
    const category = (document.getElementById('category') ? document.getElementById('category').value.trim() : '');
    const description = (document.getElementById('description') ? document.getElementById('description').value.trim() : '');
    const problem = (document.getElementById('problem_statement') ? document.getElementById('problem_statement').value.trim() : '');
    const solution = (document.getElementById('solution') ? document.getElementById('solution').value.trim() : '');
    
    const fileInput = document.getElementById('abstract_file');
    const hasNewFile = fileInput && fileInput.files && fileInput.files.length > 0;
    const githubUrl = (document.getElementById('github_url') ? document.getElementById('github_url').value.trim() : '');
    const driveUrl = (document.getElementById('drive_url') ? document.getElementById('drive_url').value.trim() : '');

    const hasTitle = (title.length >= 4 && category.length > 0);
    const hasDesc = (description.split(/\s+/).filter(Boolean).length >= 8 || description.length >= 30);
    const hasProblem = (problem.length >= 15);
    const hasSolution = (solution.length >= 15);
    const hasAttachments = (hasNewFile || !!existingAbstractDocUrl || githubUrl.length > 0 || driveUrl.length > 0);

    const checks = [
      { id: 'chk-title', passed: hasTitle },
      { id: 'chk-desc', passed: hasDesc },
      { id: 'chk-problem', passed: hasProblem },
      { id: 'chk-solution', passed: hasSolution },
      { id: 'chk-attachments', passed: hasAttachments },
    ];

    let passedCount = 0;
    checks.forEach(c => {
      const el = document.getElementById(c.id);
      if (el) {
        const icon = el.querySelector('.chk-icon');
        if (c.passed) {
          passedCount++;
          el.style.color = '#15803d';
          el.style.fontWeight = '600';
          if (icon) icon.textContent = '🟢';
        } else {
          el.style.color = 'var(--text-muted)';
          el.style.fontWeight = 'normal';
          if (icon) icon.textContent = '⚪';
        }
      }
    });

    const score = Math.round((passedCount / checks.length) * 100);
    const scoreBadge = document.getElementById('pitch-score-badge');
    if (scoreBadge) {
      scoreBadge.textContent = `${score}%`;
      scoreBadge.style.color = score === 100 ? '#16a34a' : 'var(--primary)';
    }

    const progressBar = document.getElementById('pitch-progress-bar');
    if (progressBar) {
      progressBar.style.width = `${score}%`;
      if (score === 100) {
        progressBar.style.background = 'linear-gradient(90deg, #22c55e, #16a34a)';
      } else {
        progressBar.style.background = 'linear-gradient(90deg, #f97316, #ea580c)';
      }
    }
  }

  // Attach live listeners for pitch score
  ['input', 'change', 'keyup'].forEach(evt => {
    form.addEventListener(evt, updateReadinessScore);
  });
  updateReadinessScore();

  // Submission handler function
  async function submitIdeaWithStatus(targetStatus) {
    const btnDraft = document.getElementById('btn-save-draft');
    const btnSubmit = document.getElementById('btn-submit-review');

    const titleVal = document.getElementById('title').value.trim();
    if (!titleVal) {
      utils.showToast('Please enter an idea title.', 'error');
      document.getElementById('title').focus();
      return;
    }

    if (targetStatus === 'submitted') {
      const descVal = document.getElementById('description').value.trim();
      if (!descVal) {
        utils.showToast('Please provide an elevator pitch before submitting for review.', 'error');
        document.getElementById('description').focus();
        return;
      }
    }

    if (btnDraft) btnDraft.disabled = true;
    if (btnSubmit) btnSubmit.disabled = true;

    try {
      let uploadedAbstractUrl = existingAbstractDocUrl;
      const fileInput = document.getElementById('abstract_file');

      // Upload file if selected
      if (fileInput && fileInput.files && fileInput.files.length > 0) {
        const formData = new FormData();
        formData.append('file', fileInput.files[0]);
        const uploadRes = await api.post('/ideas/upload-abstract', formData);
        if (uploadRes.success && uploadRes.data && uploadRes.data.file_url) {
          uploadedAbstractUrl = uploadRes.data.file_url;
        }
      }

      const payload = {
        title: titleVal,
        description: document.getElementById('description').value.trim(),
        problem_statement: document.getElementById('problem_statement').value.trim(),
        solution: document.getElementById('solution').value.trim(),
        category: document.getElementById('category').value.trim(),
        tags: document.getElementById('tags').value.trim(),
        github_url: (document.getElementById('github_url') ? document.getElementById('github_url').value.trim() : '') || null,
        drive_url: (document.getElementById('drive_url') ? document.getElementById('drive_url').value.trim() : '') || null,
        abstract_doc_url: uploadedAbstractUrl,
        status: targetStatus
      };

      if (isEdit) {
        await api.put(`/ideas/${ideaId}`, payload);
        const successMsg = targetStatus === 'draft' ? 'Idea saved as draft!' : 'Idea submitted for review!';
        utils.showToast(successMsg, 'success');
      } else {
        await api.post('/ideas', payload);
        const successMsg = targetStatus === 'draft' ? 'Idea created and saved as draft!' : 'Idea created and submitted for review!';
        utils.showToast(successMsg, 'success');
      }

      setTimeout(() => {
        window.location.href = '/student/ideas.html';
      }, 750);
    } catch (err) {
      utils.showToast(err.message || 'Operation failed', 'error');
      if (btnDraft) btnDraft.disabled = false;
      if (btnSubmit) btnSubmit.disabled = false;
    }
  }

  // Wire up action buttons
  const btnSaveDraft = document.getElementById('btn-save-draft');
  if (btnSaveDraft) {
    btnSaveDraft.addEventListener('click', (e) => {
      e.preventDefault();
      submitIdeaWithStatus('draft');
    });
  }

  const btnSubmitReview = document.getElementById('btn-submit-review');
  if (btnSubmitReview) {
    btnSubmitReview.addEventListener('click', (e) => {
      e.preventDefault();
      submitIdeaWithStatus('submitted');
    });
  }

  form.addEventListener('submit', (e) => {
    e.preventDefault();
    submitIdeaWithStatus('submitted');
  });
});


