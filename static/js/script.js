/**
 * script.js - Client-side interactions for FindIt Portal
 */

document.addEventListener('DOMContentLoaded', () => {
  // 1. Mobile Menu Toggle
  const mobileToggle = document.getElementById('mobile-toggle');
  const navLinks = document.getElementById('nav-links');

  if (mobileToggle && navLinks) {
    mobileToggle.addEventListener('click', () => {
      const isExpanded = mobileToggle.getAttribute('aria-expanded') === 'true';
      mobileToggle.setAttribute('aria-expanded', !isExpanded);
      navLinks.classList.toggle('open');
    });
  }

  // 2. Flash Messages Dismissal
  const flashAlerts = document.querySelectorAll('.flash-alert');
  flashAlerts.forEach((alert) => {
    // Close button click
    const closeBtn = alert.querySelector('.flash-close');
    if (closeBtn) {
      closeBtn.addEventListener('click', () => {
        alert.style.opacity = '0';
        setTimeout(() => alert.remove(), 250);
      });
    }

    // Auto-dismiss after 6 seconds
    setTimeout(() => {
      if (document.body.contains(alert)) {
        alert.style.transition = 'opacity 0.4s ease';
        alert.style.opacity = '0';
        setTimeout(() => alert.remove(), 400);
      }
    }, 6000);
  });

  // 3. Image File Upload Preview
  const imageInput = document.getElementById('image');
  const previewContainer = document.getElementById('image-preview-container');
  const previewImg = document.getElementById('image-preview');
  const uploadPrompt = document.getElementById('upload-prompt-text');

  if (imageInput) {
    imageInput.addEventListener('change', function () {
      const file = this.files[0];
      if (file) {
        // Validate file size client-side (5MB max)
        if (file.size > 5 * 1024 * 1024) {
          alert('File size exceeds the 5MB limit. Please choose a smaller image.');
          this.value = '';
          if (previewContainer) previewContainer.style.display = 'none';
          if (uploadPrompt) uploadPrompt.textContent = 'Choose an image file (optional)';
          return;
        }

        const reader = new FileReader();
        reader.onload = function (e) {
          if (previewImg && previewContainer) {
            previewImg.src = e.target.result;
            previewContainer.style.display = 'block';
          }
          if (uploadPrompt) {
            uploadPrompt.textContent = `Selected: ${file.name}`;
          }
        };
        reader.readAsDataURL(file);
      } else {
        if (previewContainer) previewContainer.style.display = 'none';
        if (uploadPrompt) uploadPrompt.textContent = 'Choose an image file (optional)';
      }
    });
  }

  // 4. Default today's date if date field is empty
  const dateInput = document.getElementById('item_date');
  if (dateInput && !dateInput.value) {
    const today = new Date().toISOString().split('T')[0];
    dateInput.value = today;
    dateInput.max = today; // Do not allow future dates for lost/found reports
  }
});
