document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('registerForm');
  const message = document.getElementById('message');
  const submitButton = form.querySelector('button[type="submit"]');

  form.addEventListener('submit', async (event) => {
    event.preventDefault();

    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value.trim();
    if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      message.textContent = 'Enter a valid email address.';
      return;
    }
    if (password.length < 8) {
      message.textContent = 'Password must be at least 8 characters.';
      return;
    }

    submitButton.disabled = true;
    message.textContent = 'Creating account...';
    try {
      await registerUser(email, password);

      window.location.href = 'login.html';
    } catch (error) {
      message.textContent = error.message || 'Registration failed.';
    } finally {
      submitButton.disabled = false;
    }
  });
});
