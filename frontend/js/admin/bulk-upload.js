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
