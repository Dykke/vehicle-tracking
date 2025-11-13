// Global functions for driver management

// Toast notification function is globally available from base.html

// Confirmation dialog
function showConfirmation(title, message, confirmCallback) {
    // Store the callback in a global variable so it's accessible from anywhere
    window.pendingAction = confirmCallback;
    
    // Update modal content
    document.getElementById('confirmationTitle').textContent = title;
    document.getElementById('confirmationMessage').innerHTML = message;
    
    // Set up confirm button
    document.getElementById('confirmButton').onclick = function() {
        if (window.pendingAction) {
            window.pendingAction();
        }
        
        // Hide modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('confirmationModal'));
        if (modal) {
            modal.hide();
        } else {
            // Fallback if modal instance not found
            document.getElementById('confirmationModal').style.display = 'none';
            document.body.classList.remove('modal-open');
            document.querySelectorAll('.modal-backdrop').forEach(el => el.remove());
        }
    };
    
    // Fix z-index issues before showing modal
    fixModalZIndex();
    
    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('confirmationModal'));
    modal.show();
    
    // Make sure modal is above backdrop
    setTimeout(fixModalZIndex, 50);
}

// Fix modal z-index issues
function fixModalZIndex() {
    // Create a style element if it doesn't exist
    let styleEl = document.getElementById('modal-fix-styles');
    if (!styleEl) {
        styleEl = document.createElement('style');
        styleEl.id = 'modal-fix-styles';
        document.head.appendChild(styleEl);
    }
    
    // Add CSS rules directly to ensure they take precedence
    styleEl.textContent = `
        .modal-backdrop {
            z-index: 1040 !important;
            opacity: 0.5 !important;
        }
        .modal {
            z-index: 1050 !important;
        }
        .modal-dialog {
            z-index: 1060 !important;
            position: relative !important;
        }
        .modal-content {
            z-index: 1070 !important;
            position: relative !important;
        }
        #confirmationModal {
            z-index: 1080 !important;
        }
        #confirmationModal .modal-dialog {
            z-index: 1090 !important;
        }
        #confirmationModal .modal-content {
            z-index: 1100 !important;
        }
        .btn-group .btn {
            z-index: 1030 !important;
            position: relative !important;
        }
        body.modal-open .container button.btn {
            z-index: 1030 !important;
        }
    `;
    
    // Remove any inline styles that might conflict
    document.querySelectorAll('.modal-backdrop').forEach(el => {
        el.removeAttribute('style');
        el.classList.add('fixed-backdrop');
    });
    
    // Set attributes for open modal
    const openModal = document.querySelector('.modal.show');
    if (openModal) {
        openModal.style.display = 'block';
        openModal.style.zIndex = '1050';
        
        // Find active dialog and content
        const dialog = openModal.querySelector('.modal-dialog');
        if (dialog) dialog.style.zIndex = '1060';
        
        const content = openModal.querySelector('.modal-content');
        if (content) content.style.zIndex = '1070';
    }
    
    // Make sure body has modal-open class
    document.body.classList.add('modal-open');
}

// View driver details
async function loadDriverDetails(driverId) {
    try {
        const response = await fetch(`/operator/drivers/${driverId}/details`);
        const data = await response.json();
        
        if (response.ok) {
            const driver = data.driver;
            
            // Update driver details in the modal
            document.getElementById('viewDriverName').textContent = driver.username;
            document.getElementById('viewDriverEmail').textContent = driver.email;
            document.getElementById('viewDriverId').textContent = driver.id;
            document.getElementById('viewDriverCreated').textContent = new Date(driver.created_at).toLocaleString();
            
            // Update status badge
            const statusBadge = document.getElementById('viewDriverStatus');
            statusBadge.textContent = driver.is_active ? 'Active' : 'Inactive';
            statusBadge.className = driver.is_active ? 'badge bg-success mb-3' : 'badge bg-danger mb-3';
            
            // Update profile image
            const profileImage = document.getElementById('profileImage');
            const profilePlaceholder = document.getElementById('profilePlaceholder');
            
            if (driver.profile_image_url) {
                profileImage.src = driver.profile_image_url;
                profileImage.style.display = 'block';
                profilePlaceholder.style.display = 'none';
            } else {
                profileImage.style.display = 'none';
                profilePlaceholder.style.display = 'flex';
            }
            
            // Format assigned vehicles data
            let vehiclesHtml = 'No vehicles assigned';
            if (data.vehicles && data.vehicles.length > 0) {
                vehiclesHtml = data.vehicles.map(v => 
                    `<span class="badge bg-info text-dark me-1 mb-1">${v.registration_number}</span>`
                ).join(' ');
            }
            document.getElementById('viewDriverVehicles').innerHTML = vehiclesHtml;
            
            // Format recent activity with better display
            let activityHtml = 'No recent activity';
            if (data.recent_activity && data.recent_activity.length > 0) {
                activityHtml = '<ul class="list-group list-group-flush">' +
                    data.recent_activity.map(a => 
                        `<li class="list-group-item bg-transparent py-1">
                            <i class="fas fa-history text-secondary me-2"></i>
                            ${a.action} 
                            <small class="text-muted">(${new Date(a.created_at).toLocaleString()})</small>
                         </li>`
                    ).join('') +
                    '</ul>';
            }
            document.getElementById('viewDriverActivity').innerHTML = activityHtml;
            
            // Fix z-index issues
            fixModalZIndex();
            
            // Show modal
            const modal = new bootstrap.Modal(document.getElementById('viewDriverModal'));
            modal.show();
            
            // Make sure z-index is correct after modal is shown
            setTimeout(fixModalZIndex, 50);
        } else {
            showToast('Error', data.error || 'Failed to load driver details.', 'error');
            console.error('Error response from backend:', data);
        }
    } catch (error) {
        console.error('Error loading driver details:', error);
        showToast('Error', 'An error occurred while loading the driver details.', 'error');
    }
}

// Edit driver
async function loadDriverForEdit(driverId) {
    try {
        const response = await fetch(`/operator/drivers/${driverId}`);
        const data = await response.json();
        
        if (response.ok) {
            document.getElementById('edit_driver_id').value = data.driver.id;
            document.getElementById('edit_username').value = data.driver.username;
            document.getElementById('edit_email').value = data.driver.email;
            document.getElementById('edit_is_active').checked = data.driver.is_active;
            
            // Fix z-index issues
            fixModalZIndex();
            
            // Show modal
            const modal = new bootstrap.Modal(document.getElementById('editDriverModal'));
            modal.show();
            
            // Make sure z-index is correct after modal is shown
            setTimeout(fixModalZIndex, 50);
        } else {
            showToast('Error', data.error || 'Failed to load driver details.', 'error');
            console.error('Error response from backend:', data);
        }
    } catch (error) {
        console.error('Error loading driver:', error);
        showToast('Error', 'An error occurred while loading the driver details.', 'error');
    }
}

// Reset password
async function loadDriverForPasswordReset(driverId) {
    try {
        const response = await fetch(`/operator/drivers/${driverId}`);
        const data = await response.json();
        
        if (response.ok) {
            // Clear any previous password inputs
            document.getElementById('new_password').value = '';
            document.getElementById('confirm_new_password').value = '';
            
            // Set driver details
            document.getElementById('reset_driver_id').value = data.driver.id;
            document.getElementById('reset_username').value = data.driver.username;
            
            // Fix z-index issues
            fixModalZIndex();
            
            // Show modal
            const modal = new bootstrap.Modal(document.getElementById('resetPasswordModal'));
            modal.show();
            
            // Make sure z-index is correct after modal is shown
            setTimeout(fixModalZIndex, 50);
        } else {
            showToast('Error', data.error || 'Failed to load driver details.', 'error');
            console.error('Error response from backend:', data);
        }
    } catch (error) {
        console.error('Error loading driver:', error);
        showToast('Error', 'An error occurred while loading the driver details.', 'error');
    }
}

// Activate driver
async function activateDriver(driverId) {
    try {
        // Close any confirmation modal
        const confirmModal = bootstrap.Modal.getInstance(document.getElementById('confirmationModal'));
        if (confirmModal) confirmModal.hide();
        
        showToast('Processing', 'Activating driver...', 'info');
        
        const response = await fetch(`/operator/drivers/${driverId}/activate`, {
            method: 'POST',
            credentials: 'same-origin'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showToast('Success', 'Driver activated successfully!', 'success');
            setTimeout(() => location.reload(), 1500);
        } else {
            showToast('Error', data.error || 'Failed to activate driver.', 'error');
            console.error('Error response from backend:', data);
        }
    } catch (error) {
        console.error('Error activating driver:', error);
        showToast('Error', 'An error occurred while activating the driver.', 'error');
    }
}

// Deactivate driver
async function deactivateDriver(driverId) {
    try {
        // Close any confirmation modal
        const confirmModal = bootstrap.Modal.getInstance(document.getElementById('confirmationModal'));
        if (confirmModal) confirmModal.hide();
        
        showToast('Processing', 'Deactivating driver...', 'info');
        
        const response = await fetch(`/operator/drivers/${driverId}/deactivate`, {
            method: 'POST',
            credentials: 'same-origin'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showToast('Success', 'Driver deactivated successfully!', 'success');
            setTimeout(() => location.reload(), 1500);
        } else {
            showToast('Error', data.error || 'Failed to deactivate driver.', 'error');
            console.error('Error response from backend:', data);
        }
    } catch (error) {
        console.error('Error deactivating driver:', error);
        showToast('Error', 'An error occurred while deactivating the driver.', 'error');
    }
}

// Update driver information
async function updateDriver(driverId, email, isActive) {
    try {
        // Show loading state
        const updateBtn = document.getElementById('updateDriverBtn');
        const originalText = updateBtn.textContent;
        updateBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Updating...';
        updateBtn.disabled = true;
        
        showToast('Processing', 'Updating driver information...', 'info');
        
        const response = await fetch(`/operator/drivers/${driverId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                email,
                is_active: isActive
            }),
            credentials: 'same-origin'
        });
        
        const data = await response.json();
        
        // Reset button state
        updateBtn.innerHTML = originalText;
        updateBtn.disabled = false;
        
        if (response.ok) {
            showToast('Success', 'Driver updated successfully!', 'success');
            
            // Close the modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('editDriverModal'));
            if (modal) modal.hide();
            
            // Reload page after a short delay
            setTimeout(() => location.reload(), 1500);
        } else {
            showToast('Error', data.error || 'Failed to update driver.', 'error');
            console.error('Error response from backend:', data);
        }
    } catch (error) {
        console.error('Error updating driver:', error);
        
        // Reset button state
        const updateBtn = document.getElementById('updateDriverBtn');
        if (updateBtn) {
            updateBtn.innerHTML = 'Update Driver';
            updateBtn.disabled = false;
        }
        
        showToast('Error', 'An error occurred while updating the driver.', 'error');
    }
}

// Reset driver password
async function resetDriverPassword(driverId, newPassword) {
    try {
        // Show loading state
        const resetBtn = document.getElementById('resetPasswordBtn');
        const originalText = resetBtn.textContent;
        resetBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Resetting...';
        resetBtn.disabled = true;
        
        showToast('Processing', 'Resetting driver password...', 'info');
        
        const response = await fetch(`/operator/drivers/${driverId}/reset-password`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                new_password: newPassword
            }),
            credentials: 'same-origin'
        });
        
        const data = await response.json();
        
        // Reset button state
        resetBtn.innerHTML = originalText;
        resetBtn.disabled = false;
        
        if (response.ok) {
            showToast('Success', 'Password reset successfully!', 'success');
            
            // Close the modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('resetPasswordModal'));
            if (modal) modal.hide();
            
            // Clear the form
            document.getElementById('new_password').value = '';
            document.getElementById('confirm_new_password').value = '';
        } else {
            showToast('Error', data.error || 'Failed to reset password.', 'error');
            console.error('Error response from backend:', data);
        }
    } catch (error) {
        console.error('Error resetting password:', error);
        
        // Reset button state
        const resetBtn = document.getElementById('resetPasswordBtn');
        if (resetBtn) {
            resetBtn.innerHTML = 'Reset Password';
            resetBtn.disabled = false;
        }
        
        showToast('Error', 'An error occurred while resetting the password.', 'error');
    }
}

// Initialize functions when page loads
document.addEventListener('DOMContentLoaded', function() {
    console.log('Driver actions script loaded');
    
    // Apply global modal fixes to ensure proper z-index stacking
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('show.bs.modal', function() {
            fixModalZIndex();
        });
        
        modal.addEventListener('shown.bs.modal', function() {
            fixModalZIndex();
        });
    });
    
    // Initialize buttons for update/edit driver
    const updateDriverBtn = document.getElementById('updateDriverBtn');
    if (updateDriverBtn) {
        // Check if this button has a custom handler already attached (from manage_drivers.html)
        if (updateDriverBtn.hasAttribute('data-custom-handler')) {
            console.log('✋ Update driver button has custom handler - SKIPPING default listener');
            console.log('This prevents double-firing and page reloads');
        } else {
            console.log('Found update driver button, attaching handler');
            updateDriverBtn.addEventListener('click', function() {
                const driverId = document.getElementById('edit_driver_id').value;
                const email = document.getElementById('edit_email').value;
                const isActive = document.getElementById('edit_is_active').checked;
                
                if (!email) {
                    showToast('Validation Error', 'Please fill in all required fields.', 'error');
                    return;
                }
                
                updateDriver(driverId, email, isActive);
            });
        }
    }
    
    // Initialize buttons for reset password
    const resetPasswordBtn = document.getElementById('resetPasswordBtn');
    if (resetPasswordBtn) {
        console.log('Found reset password button, attaching handler');
        resetPasswordBtn.addEventListener('click', function() {
            const driverId = document.getElementById('reset_driver_id').value;
            const newPassword = document.getElementById('new_password').value;
            const confirmNewPassword = document.getElementById('confirm_new_password').value;
            
            if (!newPassword || !confirmNewPassword) {
                showToast('Validation Error', 'Please fill in all required fields.', 'error');
                return;
            }
            
            if (newPassword !== confirmNewPassword) {
                showToast('Validation Error', 'Passwords do not match.', 'error');
                return;
            }
            
            resetDriverPassword(driverId, newPassword);
        });
    }
});
