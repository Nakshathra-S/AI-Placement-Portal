// Authentication JavaScript Handler (Login & Register)
document.addEventListener('DOMContentLoaded', () => {
  const loginForm = document.getElementById('loginForm');
  const registerForm = document.getElementById('registerForm');
  const alertBox = document.getElementById('authAlert');

  function showAlert(message, isSuccess = false) {
    if (!alertBox) return;
    alertBox.textContent = message;
    alertBox.className = `alert-box ${isSuccess ? 'alert-success' : 'alert-danger'} show`;
  }

  function hideAlert() {
    if (!alertBox) return;
    alertBox.className = 'alert-box';
    alertBox.textContent = '';
  }

  // Handle Login
  if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      hideAlert();

      const email = document.getElementById('email').value.trim();
      const password = document.getElementById('password').value;
      const submitBtn = document.getElementById('submitBtn');

      if (!email || !password) {
        showAlert('Please fill in both email and password.');
        return;
      }

      // UI loading state
      const originalBtnText = submitBtn.innerHTML;
      submitBtn.disabled = true;
      submitBtn.innerHTML = '<span class="spinner"></span> Signing In...';

      try {
        const response = await fetch('/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, password })
        });

        const data = await response.json();

        if (response.ok && data.success) {
          window.location.href = data.redirect || '/dashboard';
        } else {
          showAlert(data.message || 'Invalid credentials. Please verify your email and password.');
          submitBtn.disabled = false;
          submitBtn.innerHTML = originalBtnText;
        }
      } catch (err) {
        showAlert('Network or server error. Please ensure the backend is running.');
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalBtnText;
      }
    });
  }

  // Handle Register
  if (registerForm) {
    registerForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      hideAlert();

      const name = document.getElementById('name').value.trim();
      const email = document.getElementById('email').value.trim();
      const password = document.getElementById('password').value;
      const confirmPassword = document.getElementById('confirm_password').value;
      const submitBtn = document.getElementById('submitBtn');

      if (!name || !email || !password || !confirmPassword) {
        showAlert('Please fill in all registration fields.');
        return;
      }

      if (password !== confirmPassword) {
        showAlert('Passwords do not match. Please re-enter.');
        return;
      }

      if (password.length < 6) {
        showAlert('Password must contain at least 6 characters.');
        return;
      }

      // UI loading state
      const originalBtnText = submitBtn.innerHTML;
      submitBtn.disabled = true;
      submitBtn.innerHTML = '<span class="spinner"></span> Creating Account...';

      try {
        const response = await fetch('/register', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            name,
            email,
            password,
            confirm_password: confirmPassword
          })
        });

        const data = await response.json();

        if (response.ok && data.success) {
          window.location.href = data.redirect || '/dashboard';
        } else {
          showAlert(data.message || 'Registration failed. Email may already be in use.');
          submitBtn.disabled = false;
          submitBtn.innerHTML = originalBtnText;
        }
      } catch (err) {
        showAlert('Network or server error during registration.');
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalBtnText;
      }
    });
  }
});
