$(document).ready(function () {
    // Toggle password visibility
    $('#togglePassword').click(function () {
        const passwordInput = $('#password');
        const type = passwordInput.attr('type') === 'password' ? 'text' : 'password';
        passwordInput.attr('type', type);
        $(this).find('i').toggleClass('fa-eye-slash fa-eye');
    });

    // Handle form submission with AJAX
    $('#loginForm').submit(function (e) {
        e.preventDefault(); // Prevent default form submission
        
        // Store "Remember Me" preference before submitting
        const rememberMe = $('#rememberMe').is(':checked');
        if (rememberMe) {
            localStorage.setItem('rememberedAdmin', $('#username').val());
        } else {
            localStorage.removeItem('rememberedAdmin');
        }

        $.ajax({
            url: '/admin_login', // Flask endpoint
            method: 'POST',
            data: $(this).serialize(), // Serialize form data
            success: function(response) {
                // On success, Flask redirects to /admin_home
                window.location.href = '/admin_home';
            },
            error: function(xhr) {
                // On error, Flask will flash a message; reload to display it
                window.location.reload();
            }
        });
    });

    // Pre-fill username if "Remember Me" was checked previously
    const rememberedAdmin = localStorage.getItem('rememberedAdmin');
    if (rememberedAdmin) {
        $('#username').val(rememberedAdmin);
        $('#rememberMe').prop('checked', true);
    }

    // Forgot Password link (mock behavior)
    $('#forgotPassword').click(function (e) {
        e.preventDefault();
        alert('Please contact support at support@kanaakshoes.com to reset your password.');
    });
});