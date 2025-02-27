$(document).ready(function () {
    $('.navbar-toggler').click(function () {
        $('#sidebar').toggleClass('show');
    });

    $(document).click(function (event) {
        if ($(window).width() <= 768) {
            if (!$('#sidebar').is(event.target) && $('#sidebar').has(event.target).length === 0 && !$('.navbar-toggler').is(event.target)) {
                $('#sidebar').removeClass('show');
            }
        }
    });

    $('.nav-link, .dropdown-item').click(function (e) {
        e.preventDefault();
        const target = $(this).attr('href').substring(1);
        if (target !== '') {  // Ignore empty href from Change Password link
            $('.section').hide();
            $(`#${target}`).show();
            $('.nav-link').removeClass('active');
            $(this).addClass('active');
        }
    });

    $('#dashboard').show();

    $('.edit-order-btn').on('click', function() {
        const orderId = $(this).data('id');
        const status = $(this).data('status');
        $('#editOrderId').val(orderId);
        $('#editOrderStatus').val(status);
    });

    $('.edit-user-btn').on('click', function() {
        const userId = $(this).data('id');
        const name = $(this).data('name');
        const email = $(this).data('email');
        $('#editUserId').val(userId);
        $('#editUserName').val(name);
        $('#editUserEmail').val(email);
    });

    $('#productForm').submit(function (e) {
        e.preventDefault();
        const formData = new FormData(this);
        $.ajax({
            url: '/add_product',
            method: 'POST',
            data: formData,
            contentType: false,
            processData: false,
            success: function(response) {
                if (response.success) {
                    alert(response.message);
                    $('#productForm')[0].reset();
                    location.reload();
                } else {
                    alert(response.message);
                }
            },
            error: function() {
                alert('Error adding product.');
            }
        });
    });

    $('.delete-product-btn').on('click', function() {
        const productId = $(this).data('id');
        if (confirm('Are you sure you want to delete this product?')) {
            $.ajax({
                url: '/delete_product',
                method: 'POST',
                data: { product_id: productId },
                success: function(response) {
                    if (response.success) {
                        alert(response.message);
                        location.reload();
                    } else {
                        alert(response.message);
                    }
                },
                error: function() {
                    alert('Error deleting product.');
                }
            });
        }
    });

    $('#addOrderForm').submit(function (e) {
        e.preventDefault();
        $.ajax({
            url: '/add_order',
            method: 'POST',
            data: $(this).serialize(),
            success: function(response) {
                if (response.success) {
                    alert(response.message);
                    $('#addOrderForm')[0].reset();
                    $('#addOrderModal').modal('hide');
                    location.reload();
                } else {
                    alert(response.message);
                }
            },
            error: function() {
                alert('Error adding order.');
            }
        });
    });

    $('#editOrderForm').submit(function (e) {
        e.preventDefault();
        $.ajax({
            url: '/update_order',
            method: 'POST',
            data: $(this).serialize(),
            success: function(response) {
                if (response.success) {
                    alert(response.message);
                    $('#editOrderModal').modal('hide');
                    location.reload();
                } else {
                    alert(response.message);
                }
            },
            error: function() {
                alert('Error updating order.');
            }
        });
    });

    $('#addUserForm').submit(function (e) {
        e.preventDefault();
        $.ajax({
            url: '/add_user',
            method: 'POST',
            data: $(this).serialize(),
            success: function(response) {
                if (response.success) {
                    alert(response.message);
                    $('#addUserForm')[0].reset();
                    $('#addUserModal').modal('hide');
                    location.reload();
                } else {
                    alert(response.message);
                }
            },
            error: function() {
                alert('Error adding user.');
            }
        });
    });

    $('#editUserForm').submit(function (e) {
        e.preventDefault();
        $.ajax({
            url: '/update_user',
            method: 'POST',
            data: $(this).serialize(),
            success: function(response) {
                if (response.success) {
                    alert(response.message);
                    $('#editUserModal').modal('hide');
                    location.reload();
                } else {
                    alert(response.message);
                }
            },
            error: function() {
                alert('Error updating user.');
            }
        });
    });

    $('#addSaleForm').submit(function (e) {
        e.preventDefault();
        $.ajax({
            url: '/add_sale',
            method: 'POST',
            data: $(this).serialize(),
            success: function(response) {
                if (response.success) {
                    alert(response.message);
                    $('#addSaleForm')[0].reset();
                    $('#addSaleModal').modal('hide');
                    location.reload();
                } else {
                    alert(response.message);
                }
            },
            error: function() {
                alert('Error adding sale.');
            }
        });
    });

    $('#replyMessageForm').submit(function (e) {
        e.preventDefault();
        $.ajax({
            url: '/add_contact_reply',
            method: 'POST',
            data: $(this).serialize(),
            success: function(response) {
                if (response.success) {
                    alert(response.message);
                    $('#replyMessageForm')[0].reset();
                    $('#replyMessageModal').modal('hide');
                } else {
                    alert(response.message);
                }
            },
            error: function() {
                alert('Error sending reply.');
            }
        });
    });

    $('#addRefundForm').submit(function (e) {
        e.preventDefault();
        $.ajax({
            url: '/add_refund',
            method: 'POST',
            data: $(this).serialize(),
            success: function(response) {
                if (response.success) {
                    alert(response.message);
                    $('#addRefundForm')[0].reset();
                    $('#addRefundModal').modal('hide');
                    location.reload();
                } else {
                    alert(response.message);
                }
            },
            error: function() {
                alert('Error processing refund.');
            }
        });
    });

    // Handle Admin Change Password Form Submission
    $('#changePasswordForm').submit(function (e) {
        e.preventDefault();
        const newPassword = $('#newPassword').val();
        const confirmPassword = $('#confirmPassword').val();
        
        if (newPassword !== confirmPassword) {
            alert('New password and confirmation do not match!');
            return;
        }

        $.ajax({
            url: '/admin_change_password',
            method: 'POST',
            data: $(this).serialize(),
            success: function(response) {
                if (response.success) {
                    alert(response.message);
                    $('#changePasswordForm')[0].reset();
                    $('#changePasswordModal').modal('hide');
                } else {
                    alert(response.message);
                }
            },
            error: function() {
                alert('Error changing password.');
            }
        });
    });
});