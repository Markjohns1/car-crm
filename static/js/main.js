/**
 * SafiWash CRM - Main JavaScript
 * Handles sidebar toggle and other interactive features
 */

document.addEventListener('DOMContentLoaded', function () {
    // Sidebar toggle functionality
    const sidebarCollapse = document.getElementById('sidebarCollapse');
    const sidebar = document.getElementById('sidebar');
    const content = document.getElementById('content');

    if (sidebarCollapse) {
        sidebarCollapse.addEventListener('click', function () {
            // Toggle collapsed mode for sidebar and content margin
            sidebar.classList.toggle('collapsed');
            content.classList.toggle('collapsed-margin');

            // On mobile, sidebar is hidden and we use bottom nav, 
            // but the toggle button can still be used for other purposes if needed.
        });
    }

    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = new bootstrap.Alert(alert);
            if (bsAlert) bsAlert.close();
        }, 5000);
    });

    // Handle M-Pesa/Card "Nice Pop up" (Future Upgrade placeholder)
    // Adding listeners to payment radios to show a toast or small info
    const paymentRadios = document.querySelectorAll('input[name="payment_method"]');
    paymentRadios.forEach(radio => {
        radio.addEventListener('change', function () {
            if (this.value === 'M-Pesa' || this.value === 'Card') {
                console.log(`${this.value} payment selected. Nice pop-up interface coming soon.`);
            }
        });
    });

    // License Plate Formatting (Uppercase + Space after letters)
    const plateInputs = document.querySelectorAll('input[name="plate_number"]');
    plateInputs.forEach(input => {
        input.addEventListener('input', function () {
            let cursorPosition = this.selectionStart;
            let originalValue = this.value;

            // Format logic
            let clean = this.value.toUpperCase().replace(/[^A-Z0-9]/g, '');
            let match = clean.match(/^([A-Z]+)([0-9].*)?$/);

            if (match && match[1] && match[2]) {
                this.value = match[1] + ' ' + match[2];
            } else {
                this.value = clean;
            }

            // Simple cursor management
            if (originalValue.length < this.value.length && this.value[cursorPosition - 1] === ' ') {
                this.setSelectionRange(cursorPosition + 1, cursorPosition + 1);
            }
        });
    });
});
