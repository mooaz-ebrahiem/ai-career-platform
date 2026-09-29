document.addEventListener('DOMContentLoaded', async () => {
  if (!getAuthHeaders()) {
    window.location.href = 'login.html';
    return;
  }

  const form = document.getElementById('questionForm');
  const select = document.getElementById('resumeChoice');
  const message = document.getElementById('questionMessage');
  const answerPanel = document.getElementById('answerPanel');
  const submitButton = form.querySelector('button[type="submit"]');

  document.querySelector('.logout').addEventListener('click', () => {
    localStorage.removeItem('access_token');
    window.location.href = 'login.html';
  });

  try {
    const resumes = await listResumes();
    select.replaceChildren();
    if (!resumes.length) {
      const option = document.createElement('option');
      option.textContent = 'Upload a resume first';
      option.value = '';
      option.disabled = true;
      option.selected = true;
      select.appendChild(option);
      submitButton.disabled = true;
      message.textContent = 'No resumes yet. Upload one before asking a question.';
      return;
    }
    resumes.forEach((resume) => {
      const option = document.createElement('option');
      option.value = resume.id;
      option.textContent = resume.filename;
      select.appendChild(option);
    });
  } catch (error) {
    message.textContent = error.message || 'Could not load your resumes.';
    submitButton.disabled = true;
    return;
  }

  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    const question = document.getElementById('question').value.trim();
    submitButton.disabled = true;
    submitButton.textContent = 'Thinking...';
    message.textContent = 'Searching your resume...';
    answerPanel.hidden = true;

    try {
      const result = await askResumeQuestion(Number(select.value), question);
      document.getElementById('askedQuestion').textContent = question;
      document.getElementById('answer').textContent = result.answer || 'That information was not found in this resume.';
      renderSources(result.sources || []);
      answerPanel.hidden = false;
      message.textContent = result.status === 'no_context'
        ? 'No matching resume section was found.'
        : 'Answer ready.';
    } catch (error) {
      message.textContent = error.message || 'The resume assistant is unavailable.';
    } finally {
      submitButton.disabled = false;
      submitButton.textContent = 'Ask question';
    }
  });

  function renderSources(sourceValues) {
    const sourcesPanel = document.getElementById('sourcesPanel');
    const sourceList = document.getElementById('sources');
    sourceList.replaceChildren();
    sourceValues.forEach((source) => {
      const item = document.createElement('li');
      item.textContent = source.text || 'Resume excerpt';
      sourceList.appendChild(item);
    });
    sourcesPanel.hidden = sourceValues.length === 0;
  }
});
