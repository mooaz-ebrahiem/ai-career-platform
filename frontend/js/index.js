document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('resumeForm');
  const message = document.getElementById('message');
  const analysisResult = document.getElementById('analysisResult');
  const analysisDetails = document.getElementById('analysisDetails');
  const tokenHeaders = getAuthHeaders();

  if (!tokenHeaders) {
    window.location.href = 'login.html';
    return;
  }

  document.querySelector('.logout').addEventListener('click', () => {
    localStorage.removeItem('access_token');
    window.location.href = 'login.html';
  });

  form.addEventListener('submit', async (event) => {
    event.preventDefault();

    const fileInput = document.getElementById('resumeFile');
    const file = fileInput.files[0];

    if (!file) {
      message.textContent = 'Please choose a PDF or DOCX file first.';
      message.classList.add('error');
      return;
    }

    if (!/\.pdf$/i.test(file.name) || (file.type && file.type !== 'application/pdf')) {
      message.textContent = 'Only PDF files are supported.';
      message.classList.add('error');
      return;
    }

    if (file.size > 5 * 1024 * 1024) {
      message.textContent = 'The file must be 5 MB or smaller.';
      message.classList.add('error');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
      const submitButton = form.querySelector('button[type="submit"]');
      submitButton.disabled = true;
      submitButton.textContent = 'Uploading and analysing...';
      message.textContent = 'Uploading and analysing... this can take up to a minute.';
      message.classList.remove('error');

      const data = await uploadResume(formData);
      localStorage.setItem('latest_resume_analysis', JSON.stringify({
        resumeId: data.resume_id,
        filename: data.filename,
        analysisResult: data.analysis_result
      }));
      if (data.analysis_result?.status !== 'complete') {
        localStorage.setItem('latest_upload_notice', 'Resume uploaded, but AI analysis is currently unavailable.');
      } else {
        localStorage.removeItem('latest_upload_notice');
      }
      window.location.href = 'dashboard.html';
    } catch (error) {
      analysisResult.hidden = true;
      message.textContent = error.message || 'Upload failed';
      message.classList.add('error');
      form.querySelector('button[type="submit"]').disabled = false;
      form.querySelector('button[type="submit"]').textContent = 'Upload';
      if (error.status === 401) {
        localStorage.removeItem('access_token');
        window.location.href = 'login.html';
      }
    }
  });
});
