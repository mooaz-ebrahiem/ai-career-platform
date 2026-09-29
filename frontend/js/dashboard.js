document.addEventListener('DOMContentLoaded', async () => {
  if (!getAuthHeaders()) {
    window.location.href = 'login.html';
    return;
  }

  const message = document.getElementById('dashboardMessage');
  const resumeList = document.getElementById('resumeList');
  const emptyResumes = document.getElementById('emptyResumes');
  const analysisNotice = document.getElementById('analysisNotice');
  const analysisPanel = document.getElementById('analysisPanel');
  message.textContent = 'Loading dashboard...';

  document.querySelector('.logout').addEventListener('click', () => {
    localStorage.removeItem('access_token');
    window.location.href = 'login.html';
  });

  function getStoredAnalysis() {
    const stored = localStorage.getItem('latest_resume_analysis');
    if (!stored) {
      return null;
    }

    try {
      const record = JSON.parse(stored);
      return record.analysisResult?.status === 'complete'
        ? record.analysisResult.analysis
        : null;
    } catch (error) {
      return null;
    }
  }

  function renderCompleteness(analysis) {
    const scoreElement = document.getElementById('resumeScore');
    if (!analysis) {
      scoreElement.textContent = '0/100';
      return;
    }

    const hasName = Boolean(analysis.full_name?.trim());
    const skillsCount = Array.isArray(analysis.main_skills) ? analysis.main_skills.filter(Boolean).length : 0;
    const hasEducation = Array.isArray(analysis.education) && analysis.education.some(Boolean);
    const hasExperience = Boolean(analysis.experience_years?.trim() && analysis.experience_years !== 'Not specified');
    const summaryLength = analysis.summary?.trim().length || 0;
    const score = (hasName ? 20 : 0)
      + Math.min(skillsCount, 5) * 6
      + (hasEducation ? 15 : 0)
      + (hasExperience ? 15 : 0)
      + Math.min(summaryLength / 200, 1) * 20;
    scoreElement.textContent = `${Math.round(score)}/100`;
  }

  function renderInsights(analysis) {
    const insightList = document.getElementById('insightList');
    insightList.replaceChildren();
    if (!analysis) {
      const item = document.createElement('li');
      item.textContent = 'Upload a resume to generate completeness insights.';
      insightList.appendChild(item);
      return;
    }

    const skills = Array.isArray(analysis.main_skills) ? analysis.main_skills.filter(Boolean) : [];
    const missing = [];
    if (!analysis.full_name?.trim()) missing.push('name');
    if (!skills.length) missing.push('skills');
    if (!analysis.education?.length) missing.push('education');
    if (!analysis.experience_years?.trim() || analysis.experience_years === 'Not specified') missing.push('experience');
    if (!analysis.summary?.trim()) missing.push('summary');

    const insights = [
      skills.length ? `Top skills: ${skills.slice(0, 3).join(', ')}.` : 'No technical skills were identified.',
      analysis.summary?.trim() ? `Summary: ${analysis.summary.trim().slice(0, 100)}${analysis.summary.trim().length > 100 ? '...' : ''}` : 'Add a concise professional summary.',
      missing.length ? `Missing sections: ${missing.join(', ')}.` : 'All main resume sections are present.',
    ];
    insights.forEach((insight) => {
      const item = document.createElement('li');
      item.textContent = insight;
      insightList.appendChild(item);
    });
  }

  function renderRecommendations(value) {
    const recommendations = document.getElementById('careerMatches');
    const note = document.getElementById('careerMatchesNote');
    if (Array.isArray(value) && value.length) {
      recommendations.textContent = value.join(', ');
      note.textContent = 'Suggested roles already stored by the backend.';
    } else if (typeof value === 'string' && value.trim()) {
      recommendations.textContent = value;
      note.textContent = 'Suggested roles already stored by the backend.';
    } else {
      recommendations.textContent = 'No recommendations stored';
      note.textContent = 'Career advice is not available from the backend yet.';
    }
  }

  function renderAnalysis() {
    const analysis = getStoredAnalysis();
    if (!analysis) {
      analysisNotice.textContent = localStorage.getItem('latest_upload_notice') || 'Upload a resume to see its analysis here.';
      renderCompleteness(null);
      renderInsights(null);
      return;
    }

    document.getElementById('analysisName').textContent = analysis.full_name || 'Name not identified';
    document.getElementById('analysisEducation').textContent = analysis.education?.join(', ') || 'Not identified';
    document.getElementById('analysisExperience').textContent = analysis.experience_years || 'Not specified';
    document.getElementById('analysisSummary').textContent = analysis.summary || 'No summary available.';
    const skills = document.getElementById('analysisSkills');
    skills.replaceChildren();
    (analysis.main_skills || []).forEach((skill) => {
      const chip = document.createElement('span');
      chip.className = 'chip';
      chip.textContent = skill;
      skills.appendChild(chip);
    });
    analysisNotice.textContent = '';
    analysisPanel.hidden = false;
    renderCompleteness(analysis);
    renderInsights(analysis);
  }

  try {
    const [stats, resumes] = await Promise.all([getDashboardStats(), listResumes()]);
    document.getElementById('userEmail').textContent = stats.user_email || 'User';
    document.getElementById('totalResumes').textContent = stats.total_resumes ?? 0;
    renderRecommendations(stats.career_matches);

    resumeList.replaceChildren();
    emptyResumes.hidden = resumes.length > 0;
    resumes.forEach((resume) => {
      const item = document.createElement('article');
      item.className = 'resume-item';
      const name = document.createElement('strong');
      name.textContent = resume.filename;
      const meta = document.createElement('span');
      meta.textContent = 'Uploaded resume';
      item.append(name, meta);
      resumeList.appendChild(item);
    });
    message.textContent = '';
    renderAnalysis();
  } catch (error) {
    message.textContent = error.message || 'Failed to load dashboard data.';
  }
});
