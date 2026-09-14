/**
 * admin/bulk-upload.js – CSV drag-and-drop batch student onboarding
 */

document.addEventListener('DOMContentLoaded', () => {
  if (!auth.requireAuth('admin')) return;

  const dropzone = document.getElementById('csv-dropzone');
  const fileInput = document.getElementById('csv-file');
  const uploadBtn = document.getElementById('btn-process-upload');
  const resultCard = document.getElementById('upload-result-card');

  const btnDownloadTop = document.getElementById('btn-download-template-top');
  const btnDownload = document.getElementById('btn-download-template');

  function downloadStudentCsvTemplate() {
    const csvContent = "email,full_name,roll_number,department,year_of_study,phone\n" +
      "alex.rivera@college.edu,Alex Rivera,21CS101,Computer Science,3,+91 9876543210\n" +
      "sarah.chen@college.edu,Sarah Chen,21EC102,Electronics & Communication,3,+91 9876543211\n" +
      "rohan.sharma@college.edu,Rohan Sharma,22ME103,Mechanical Engineering,2,+91 9876543212\n" +
      "ananya.iyer@college.edu,Ananya Iyer,23IT104,Information Technology,1,+91 9876543213\n";

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', 'eideaforge_student_template.csv');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    utils.showToast('Student CSV template downloaded!', 'success');
  }

  if (btnDownloadTop) btnDownloadTop.addEventListener('click', downloadStudentCsvTemplate);
  if (btnDownload) btnDownload.addEventListener('click', downloadStudentCsvTemplate);

  dropzone.addEventListener('click', () => fileInput.click());

  dropzone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropzone.classList.add('dragover');
  });

  dropzone.addEventListener('dragleave', () => dropzone.classList.remove('dragover'));

  dropzone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropzone.classList.remove('dragover');
    if (e.dataTransfer.files.length > 0) {
      fileInput.files = e.dataTransfer.files;
      handleFileSelected();
    }
  });

  fileInput.addEventListener('change', handleFileSelected);

  function handleFileSelected() {
    if (fileInput.files.length > 0) {
      document.getElementById('selected-filename').textContent = `📄 Selected: ${fileInput.files[0].name}`;
      uploadBtn.disabled = false;
    }
  }

  const btnDownloadCreds = document.getElementById('btn-download-credentials');
  const credsContainer = document.getElementById('credentials-table-container');
  const credsTbody = document.getElementById('credentials-tbody');

  let lastGeneratedCreds = [];
  let lastCredsFilename = '';

  function downloadGeneratedCredentials() {
    if (!lastGeneratedCreds || lastGeneratedCreds.length === 0) {
      utils.showToast('No credentials available to download', 'warning');
      return;
    }

    let csvContent = "Name,Email,Temporary Password,Roll Number,Department,Year of Study\n";
    lastGeneratedCreds.forEach(c => {
      const name = `"${(c.name || '').replace(/"/g, '""')}"`;
      const email = `"${(c.email || '').replace(/"/g, '""')}"`;
      const pw = `"${(c.temp_password || '').replace(/"/g, '""')}"`;
      const roll = `"${(c.roll_number || '').replace(/"/g, '""')}"`;
      const dept = `"${(c.department || '').replace(/"/g, '""')}"`;
      const yr = `"${(c.year_of_study || '').replace(/"/g, '""')}"`;
      csvContent += `${name},${email},${pw},${roll},${dept},${yr}\n`;
    });

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', lastCredsFilename || `student_credentials_${Date.now()}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    utils.showToast('Credentials spreadsheet downloaded!', 'success');
  }

  if (btnDownloadCreds) {
    btnDownloadCreds.addEventListener('click', downloadGeneratedCredentials);
  }

  uploadBtn.addEventListener('click', async () => {
    if (fileInput.files.length === 0) return;

    uploadBtn.disabled = true;
    uploadBtn.textContent = 'Processing CSV batch...';

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    try {
      const res = await api.post('/admin/students/bulk-upload', formData);
      if (res.success && res.data) {
        resultCard.style.display = 'block';
        document.getElementById('res-created').textContent = res.data.created || 0;
        document.getElementById('res-skipped').textContent = res.data.skipped || 0;

        lastGeneratedCreds = res.data.credentials || [];
        lastCredsFilename = res.data.credentials_file || `student_credentials_${Date.now()}.csv`;

        if (lastGeneratedCreds.length > 0) {
          credsContainer.style.display = 'block';
          credsTbody.innerHTML = lastGeneratedCreds.map(c => `
            <tr>
              <td style="font-weight:600; color:var(--text-main);">${utils.escapeHtml(c.name || 'N/A')}</td>
              <td><code>${utils.escapeHtml(c.email || 'N/A')}</code></td>
              <td><code>${utils.escapeHtml(c.roll_number || 'N/A')}</code></td>
              <td><span style="font-family:monospace; background:#fff7ed; padding:0.25rem 0.5rem; border-radius:4px; font-weight:700; color:#ea580c;">${utils.escapeHtml(c.temp_password || '')}</span></td>
              <td style="text-align:center;">
                <button class="btn btn-outline btn-sm" onclick="navigator.clipboard.writeText('${utils.escapeHtml(c.temp_password || '')}').then(() => utils.showToast('Password copied!', 'success'))" style="padding:0.25rem 0.6rem; font-size:0.75rem;">
                  📋 Copy
                </button>
              </td>
            </tr>
          `).join('');
        } else {
          credsContainer.style.display = 'none';
        }

        utils.showToast('Batch processed successfully!', 'success');
      }
    } catch (err) {
      utils.showToast(err.message || 'Upload failed', 'error');
    } finally {
      uploadBtn.disabled = false;
      uploadBtn.textContent = 'Process & Create Accounts';
    }
  });
});

