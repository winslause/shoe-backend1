document.addEventListener('DOMContentLoaded', function () {
    // Ensure jQuery is loaded
    if (typeof $ === 'undefined') {
        console.error('jQuery is not loaded. Please include it in your HTML.');
        return;
    }

    // Sidebar toggle for small devices
    const navbarToggler = document.querySelector('.navbar-toggler');
    const sidebar = document.querySelector('#sidebar');

    navbarToggler.addEventListener('click', function () {
        sidebar.classList.toggle('show');
    });

    // Close sidebar when clicking outside on mobile
    document.addEventListener('click', function (event) {
        if (window.innerWidth <= 768) {
            if (!sidebar.contains(event.target) && !navbarToggler.contains(event.target)) {
                sidebar.classList.remove('show');
            }
        }
    });

    // Fetch and populate orders dynamically
    function fetchOrders() {
        $.ajax({
            url: '/get_orders',
            method: 'GET',
            success: function(orders) {
                console.log('Orders fetched:', orders); // Debug
                const ordersTable = $('#ordersTable');
                const orderSelect = $('#orderSelect');
                ordersTable.empty();
                orderSelect.empty();
                orderSelect.append('<option value="">Choose an order</option>');

                if (Array.isArray(orders) && orders.length > 0) {
                    orders.forEach(order => {
                        // Populate orders table with cancel button (only for pending orders)
                        const cancelButton = order.status.toLowerCase() === 'pending' 
                            ? `<button class="btn btn-danger btn-sm cancel-order" data-order-id="${order.id}">Cancel Order</button>`
                            : '';
                        ordersTable.append(`
                            <tr>
                                <td>#${order.id}</td>
                                <td>${order.shoe_name || 'N/A'}</td>
                                <td>${order.order_date}</td>
                                <td>${order.status || 'Pending'}</td>
                                <td>KSh ${order.total || '0.00'}</td>
                                <td>${cancelButton}</td>
                            </tr>
                        `);

                        // Populate order select for reviews (only completed orders)
                        if (order.status.toLowerCase() === 'completed') {
                            orderSelect.append(`
                                <option value="${order.id}">${order.shoe_name || 'Order #' + order.id} (ID: ${order.id}, Status: ${order.status})</option>
                            `);
                        }
                    });

                    // Add cancel order functionality
                    $('.cancel-order').off('click').on('click', function() {
                        const orderId = $(this).data('order-id');
                        cancelOrder(orderId);
                    });
                } else {
                    ordersTable.append('<tr><td colspan="6">No orders found.</td></tr>');
                    console.log('No orders returned or user not logged in.');
                }
            },
            error: function(xhr, status, error) {
                console.error('Error fetching orders:', status, error);
                $('#ordersTable').html('<tr><td colspan="6">Error loading orders. Please try again.</td></tr>');
            }
        });
    }

    // Cancel order function
    function cancelOrder(orderId) {
        if (confirm('Are you sure you want to cancel this order?')) {
            $.ajax({
                url: '/cancel_order',
                method: 'POST',
                data: { order_id: orderId },
                success: function(response) {
                    alert(response.message);
                    if (response.success) {
                        fetchOrders(); // Refresh orders after cancellation
                    }
                },
                error: function(xhr, status, error) {
                    console.error('Cancel order error:', status, error);
                    alert('Error cancelling order. Please try again.');
                }
            });
        }
    }

    // Call fetchOrders when modals are shown
    $('#myOrdersModal, #reviewsModal').on('shown.bs.modal', function() {
        fetchOrders();
    });

    // Profile form submission
    document.getElementById('profileForm')?.addEventListener('submit', function (e) {
        e.preventDefault();
        const name = document.getElementById('name').value;
        const email = document.getElementById('email').value;
        const phone = document.getElementById('phone').value;

        $.ajax({
            url: '/update_profile',
            method: 'POST',
            data: { name: name, email: email, phone: phone },
            success: function(response) {
                alert(response.message);
                if (response.success) {
                    bootstrap.Modal.getInstance(document.getElementById('editProfileModal')).hide();
                    location.reload(); // Refresh to reflect changes
                }
            },
            error: function(xhr, status, error) {
                console.error('Profile update error:', status, error);
                alert('Error updating profile. Please try again.');
            }
        });
    });

    // Password form submission
    document.getElementById('passwordForm')?.addEventListener('submit', function (e) {
        e.preventDefault();
        const currentPassword = document.getElementById('currentPassword').value;
        const newPassword = document.getElementById('newPassword').value;
        const confirmPassword = document.getElementById('confirmPassword').value;

        if (newPassword !== confirmPassword) {
            alert('New password and confirm password do not match.');
            return;
        }

        $.ajax({
            url: '/update_password',
            method: 'POST',
            data: { current_password: currentPassword, new_password: newPassword },
            success: function(response) {
                alert(response.message);
                if (response.success) {
                    bootstrap.Modal.getInstance(document.getElementById('updatePasswordModal')).hide();
                    document.getElementById('passwordForm').reset();
                }
            },
            error: function(xhr, status, error) {
                console.error('Password update error:', status, error);
                alert('Error updating password. Please try again.');
            }
        });
    });

    // Address form submission
    document.getElementById('addressForm')?.addEventListener('submit', function (e) {
        e.preventDefault();
        const name = document.getElementById('addressName').value;
        const email = document.getElementById('addressEmail').value;
        const phone = document.getElementById('addressPhone').value;
        const address = document.getElementById('address').value;

        $.ajax({
            url: '/update_address',
            method: 'POST',
            data: { name: name, email: email, phone: phone, address: address },
            success: function(response) {
                alert(response.message);
                if (response.success) {
                    bootstrap.Modal.getInstance(document.getElementById('editAddressModal')).hide();
                    location.reload(); // Refresh to reflect changes
                }
            },
            error: function(xhr, status, error) {
                console.error('Address update error:', status, error);
                alert('Error updating address. Please try again.');
            }
        });
    });

    // Review form submission
    document.getElementById('reviewForm')?.addEventListener('submit', function (e) {
        e.preventDefault();
        const orderId = document.getElementById('orderSelect').value;
        const rating = document.getElementById('rating').value;
        const reviewText = document.getElementById('reviewText').value;

        if (!orderId) {
            alert('Please select an order to review.');
            return;
        }

        $.ajax({
            url: '/submit_review',
            method: 'POST',
            data: { order_id: orderId, rating: rating, review: reviewText },
            success: function(response) {
                alert(response.message);
                if (response.success) {
                    bootstrap.Modal.getInstance(document.getElementById('reviewsModal')).hide();
                    document.getElementById('reviewForm').reset();
                }
            },
            error: function(xhr, status, error) {
                console.error('Review submission error:', status, error);
                alert('Error submitting review. Please try again.');
            }
        });
    });
});