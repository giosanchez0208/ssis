// Popover

var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'))
var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
  return new bootstrap.Popover(popoverTriggerEl)
})

/////////////////////// AUTHENTICATION

// Function to initialize Google Sign-In
function onLoadGoogleSignin() {
  gapi.load('auth2', function() {
    const auth2 = gapi.auth2.init({
      client_id: '970350440891-0950d1pmj3vmqefhfbad0arvrn6s1ieo.apps.googleusercontent.com'
    });

    // Attach click listener to the Google Sign-In button
    document.getElementById('google-signin').addEventListener('click', () => {
      auth2.signIn()
        .then(googleUser => {
          const profile = googleUser.getBasicProfile();
          const email = profile.getEmail();

          // Validate the email format (firstname.lastname@g.msuiit.edu.ph)
          const emailRegex = /^[a-zA-Z]+\.[a-zA-Z]+@g\.msuiit\.edu\.ph$/;
          if (!emailRegex.test(email)) {
            alert('Invalid email format. Please use firstname.lastname@g.msuiit.edu.ph.');
            return;
          }

          // Handle successful Google Sign-In and redirect to students page
          window.location.href = "/students";  // You can also use Flask's url_for
        })
        .catch(error => {
          console.error("Error signing in with Google:", error);
          alert("Error signing in. Please try again.");
        });
    });
  });
}

// Handle username/password login logic
document.getElementById('login-btn').addEventListener('click', handleUsernamePasswordLogin);

function handleUsernamePasswordLogin() {
  const username = document.getElementById('username').value;
  const password = document.getElementById('password').value;

  // Check if the username follows the firstname.lastname format
  const usernameRegex = /^[a-zA-Z]+\.[a-zA-Z]+$/;
  if (!usernameRegex.test(username)) {
    alert('Invalid username format. Please use firstname.lastname.');
    return;
  }

  // You can now send the username and password to your backend for verification.
  // For example, use fetch or AJAX to make a POST request to your Flask route.

  fetch('/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      username: username,
      password: password
    })
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      window.location.href = "{{ url_for('students') }}";
    } else {
      alert('Login failed: ' + data.message);
    }
  })
  .catch(error => {
    console.error("Error during login:", error);
    alert("Login error. Please try again.");
  });
}
