// Driver Settings JavaScript
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Driver settings page initialized');
    
    // Password change form handling
    const passwordForm = document.getElementById('passwordForm');
    if (passwordForm) {
        passwordForm.addEventListener('submit', handlePasswordChange);
        console.log('✅ Password form initialized');
    } else {
        console.log('⚠️ Password form not found');
    }
    
    // Initialize export buttons
    initializeExportButtons();
});

// Handle password change
async function handlePasswordChange(event) {
    event.preventDefault();
    console.log('🔄 Password change form submitted');
    
    const currentPassword = document.getElementById('currentPassword').value;
    const newPassword = document.getElementById('newPassword').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    
    console.log('🔍 Password validation:', {
        hasCurrent: !!currentPassword,
        hasNew: !!newPassword,
        hasConfirm: !!confirmPassword,
        passwordsMatch: newPassword === confirmPassword
    });
    
    // Validation
    if (!currentPassword || !newPassword || !confirmPassword) {
        showToast('Error', 'Please fill in all password fields', 'error');
        return;
    }
    
    if (newPassword !== confirmPassword) {
        showToast('Error', 'New passwords do not match', 'error');
        return;
    }
    
    if (newPassword.length < 6) {
        showToast('Error', 'New password must be at least 6 characters long', 'error');
        return;
    }
    
    try {
        console.log('🔄 Changing password...');
        
        const response = await fetch('/driver/password', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                current_password: currentPassword,
                new_password: newPassword,
                confirm_password: confirmPassword
            })
        });
        
        const data = await response.json();
        
        if (response.ok && data.success) {
            showToast('Success', 'Password changed successfully', 'success');
            
            // Clear form
            passwordForm.reset();
            
            // Show success message
            const successAlert = document.createElement('div');
            successAlert.className = 'alert alert-success mt-3';
            successAlert.innerHTML = '<i class="fas fa-check-circle me-2"></i>Password changed successfully!';
            passwordForm.appendChild(successAlert);
            
            // Remove success message after 5 seconds
            setTimeout(() => {
                if (successAlert.parentNode) {
                    successAlert.remove();
                }
            }, 5000);
            
        } else {
            showToast('Error', data.error || 'Failed to change password', 'error');
        }
        
    } catch (error) {
        console.error('❌ Error changing password:', error);
        showToast('Error', 'Network error occurred', 'error');
    }
}

// Initialize export buttons
function initializeExportButtons() {
    // Export Trip History
    const exportTripBtn = document.getElementById('exportTripBtn');
    if (exportTripBtn) {
        exportTripBtn.addEventListener('click', exportTripHistory);
        console.log('✅ Export Trip History button initialized');
    } else {
        console.log('⚠️ Export Trip History button not found');
    }
    
    // Export Action Logs
    const exportLogsBtn = document.getElementById('exportLogsBtn');
    if (exportLogsBtn) {
        exportLogsBtn.addEventListener('click', exportActionLogs);
        console.log('✅ Export Action Logs button initialized');
    } else {
        console.log('⚠️ Export Action Logs button not found');
    }
    
    // Export Profile Data
    const exportProfileBtn = document.getElementById('exportProfileBtn');
    if (exportProfileBtn) {
        exportProfileBtn.addEventListener('click', exportProfileData);
        console.log('✅ Export Profile Data button initialized');
    } else {
        console.log('⚠️ Export Profile Data button not found');
    }
}



// Export functions
async function exportTripHistory() {
    try {
        console.log('📊 Exporting trip history...');
        showToast('Info', 'Exporting trip history...', 'info');
        
        console.log('🔍 Making request to /driver/export/trip-history');
        
        const response = await fetch('/driver/export/trip-history');
        
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `trip-history-${new Date().toISOString().split('T')[0]}.csv`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            showToast('Success', 'Trip history exported successfully', 'success');
        } else {
            const data = await response.json();
            showToast('Error', data.error || 'Failed to export trip history', 'error');
        }
        
    } catch (error) {
        console.error('❌ Error exporting trip history:', error);
        showToast('Error', 'Failed to export trip history', 'error');
    }
}

async function exportActionLogs() {
    try {
        console.log('📋 Exporting action logs...');
        showToast('Info', 'Exporting action logs...', 'info');
        
        const response = await fetch('/driver/export/action-logs');
        
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `action-logs-${new Date().toISOString().split('T')[0]}.csv`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            showToast('Success', 'Action logs exported successfully', 'success');
        } else {
            const data = await response.json();
            showToast('Error', data.error || 'Failed to export action logs', 'error');
        }
        
    } catch (error) {
        console.error('❌ Error exporting action logs:', error);
        showToast('Error', 'Failed to export action logs', 'error');
    }
}

async function exportProfileData() {
    try {
        console.log('👤 Exporting profile data...');
        showToast('Info', 'Exporting profile data...', 'info');
        
        const response = await fetch('/driver/export/profile-data');
        
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `profile-data-${new Date().toISOString().split('T')[0]}.json`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            showToast('Success', 'Profile data exported successfully', 'success');
        } else {
            const data = await response.json();
            showToast('Error', data.error || 'Failed to export profile data', 'error');
        }
        
    } catch (error) {
        console.error('❌ Error exporting profile data:', error);
        showToast('Error', 'Failed to export profile data', 'error');
    }
}



// Toast notification function is globally available from base.html
