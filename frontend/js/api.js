const API_BASE_URL = window.CAREER_API_BASE_URL || 'http://127.0.0.1:8000';

async function apiRequest(path, options = {}) {
	const headers = new Headers(options.headers || {});
	if (options.body && !(options.body instanceof FormData) && !headers.has('Content-Type')) {
		headers.set('Content-Type', 'application/json');
	}

	let response;
	try {
		response = await fetch(`${API_BASE_URL}${path}`, {
			...options,
			headers
		});
	} catch (error) {
		throw new Error('Cannot reach the server. Make sure the backend is running.');
	}
	const data = response.status === 204 ? null : await response.json().catch(() => null);

	if (!response.ok) {
		if (response.status === 401 && localStorage.getItem('access_token')) {
			localStorage.removeItem('access_token');
			window.location.href = 'login.html';
		}
		const detail = data && (data.detail || data.message);
		const message = typeof detail === 'string'
			? detail
			: Array.isArray(detail)
				? detail.map((item) => item.msg).filter(Boolean).join(' ')
				: 'The request could not be completed.';
		const error = new Error(message);
		error.status = response.status;
		throw error;
	}

	return data;
}

function getAuthHeaders() {
	const token = localStorage.getItem('access_token');
	return token ? { Authorization: `Bearer ${token}` } : null;
}

function registerUser(email, password) {
	return apiRequest('/auth/register', {
		method: 'POST',
		body: JSON.stringify({ email, password })
	});
}

function loginUser(email, password) {
	return apiRequest('/auth/login', {
		method: 'POST',
		body: JSON.stringify({ email, password })
	});
}

function getDashboardStats() {
	return apiRequest('/career/dashboard', { headers: getAuthHeaders() || {} });
}

function listResumes() {
	return apiRequest('/resumes', { headers: getAuthHeaders() || {} });
}

function uploadResume(formData) {
	return apiRequest('/resumes/upload', {
		method: 'POST',
		headers: getAuthHeaders() || {},
		body: formData
	});
}

function compareResume(resumeId, jobDescription) {
	return apiRequest('/matching/compare', {
		method: 'POST',
		headers: getAuthHeaders() || {},
		body: JSON.stringify({ resume_id: resumeId, job_description: jobDescription })
	});
}

function askResumeQuestion(resumeId, question) {
	return apiRequest(`/resumes/${resumeId}/query`, {
		method: 'POST',
		headers: getAuthHeaders() || {},
		body: JSON.stringify({ question })
	});
}
