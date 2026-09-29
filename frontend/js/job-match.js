document.addEventListener('DOMContentLoaded', async () => {
  if (!getAuthHeaders()) {
    window.location.href = 'login.html';
    return;
  }

  const form = document.getElementById('matchForm');
  const select = document.getElementById('resumeChoice');
  const message = document.getElementById('matchMessage');
  const resultPanel = document.getElementById('matchResult');
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
      message.textContent = 'No resumes yet. Upload one before running a match.';
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
    submitButton.disabled = true;
    submitButton.textContent = 'Comparing...';
    message.textContent = 'Comparing your resume...';
    resultPanel.hidden = true;

    try {
      const result = await compareResume(Number(select.value), document.getElementById('jobDescription').value.trim());
      document.getElementById('matchScore').textContent = `${result.match_score}%`;
      document.getElementById('scoreBar').style.width = `${result.match_score}%`;
      document.getElementById('recommendation').textContent = result.recommendation.replaceAll('_', ' ');
      renderUniqueList(document.getElementById('strengths'), result.strengths);
      renderUniqueList(document.getElementById('skillGaps'), result.skill_gaps);
      document.getElementById('explanation').textContent = result.explanation;
      resultPanel.hidden = false;
      message.textContent = 'Match complete.';
    } catch (error) {
      message.textContent = error.message || 'Job matching is unavailable.';
    } finally {
      submitButton.disabled = false;
      submitButton.textContent = 'Compare resume';
    }
  });

  function renderUniqueList(list, values) {
    list.replaceChildren();
    const uniqueValues = [...new Set((values || []).map((value) => value.trim()).filter(Boolean))];
    (uniqueValues.length ? uniqueValues : ['None identified']).forEach((value) => {
      const item = document.createElement('li');
      item.textContent = value;
      list.appendChild(item);
    });
  }
});
