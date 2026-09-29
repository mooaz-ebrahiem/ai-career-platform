document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('loginForm');
  const message = document.getElementById('message');
  const submitButton = form.querySelector('button[type="submit"]');

  form.addEventListener('submit', async (event) => {
    event.preventDefault();

    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value.trim();

    if (!email || !password || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      message.textContent = 'Enter a valid email and password.';
      return;
    }

    submitButton.disabled = true;
    message.textContent = 'Signing in...';
    try {
      const data = await loginUser(email, password);

      localStorage.setItem('access_token', data.access_token);
      window.location.href = 'dashboard.html';
    } catch (error) {
      message.textContent = error.message || 'Unable to sign in.';
    } finally {
      submitButton.disabled = false;
    }
  });
});
