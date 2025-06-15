// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Auto-dismiss alerts after 5 seconds
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Symptom selection enhancement for prediction form
    const symptomCheckboxes = document.querySelectorAll('.symptom-checkbox');
    if (symptomCheckboxes.length > 0) {
        const selectedSymptomsContainer = document.getElementById('selected-symptoms');
        const submitButton = document.querySelector('button[type="submit"]');

        symptomCheckboxes.forEach(function(checkbox) {
            checkbox.addEventListener('change', function() {
                updateSelectedSymptoms();
            });
        });

        function updateSelectedSymptoms() {
            selectedSymptomsContainer.innerHTML = '';
            let selectedCount = 0;

            symptomCheckboxes.forEach(function(checkbox) {
                if (checkbox.checked) {
                    selectedCount++;
                    const badge = document.createElement('span');
                    badge.className = 'badge bg-primary me-2 mb-2';
                    badge.textContent = checkbox.nextElementSibling.textContent.trim();
                    selectedSymptomsContainer.appendChild(badge);
                }
            });

            if (selectedCount > 0) {
                submitButton.disabled = false;
            } else {
                submitButton.disabled = true;
            }
        }

        // Initial update
        updateSelectedSymptoms();
    }

    // Profile picture preview
    const profilePictureInput = document.getElementById('profile-picture-input');
    const profilePicturePreview = document.getElementById('profile-picture-preview');

    if (profilePictureInput && profilePicturePreview) {
        profilePictureInput.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    profilePicturePreview.src = e.target.result;
                };
                reader.readAsDataURL(this.files[0]);
            }
        });
    }
});