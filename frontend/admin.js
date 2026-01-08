/**
 * Frontend JavaScript for Admin Panel
 * Handles ZIP file upload and processing
 */

// Dynamically set API URL based on environment
const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:5000/api'
    : `${window.location.origin}/api`;

// DOM Elements
const uploadForm = document.getElementById('uploadForm');
const examTypeSelect = document.getElementById('examType');
const examYearInput = document.getElementById('examYear');
const zipFileInput = document.getElementById('zipFile');
const fileNameDisplay = document.getElementById('fileNameDisplay');
const uploadBtn = document.getElementById('uploadBtn');
const progressSection = document.getElementById('progressSection');
const alertContainer = document.getElementById('alertContainer');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    setDefaultYear();
});

// Setup event listeners
function setupEventListeners() {
    uploadForm.addEventListener('submit', handleUpload);
    zipFileInput.addEventListener('change', handleFileSelect);
}

// Set default year to current year
function setDefaultYear() {
    const currentYear = new Date().getFullYear();
    examYearInput.value = currentYear;
}

// Handle file selection
function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) {
        const fileSizeMB = (file.size / (1024 * 1024)).toFixed(2);
        fileNameDisplay.innerHTML = `
            <strong>${file.name}</strong><br>
            <span style="font-size: 0.9rem; color: #64748b;">Size: ${fileSizeMB} MB</span>
        `;
    } else {
        fileNameDisplay.textContent = 'Click to select ZIP file';
    }
}

// Handle upload
async function handleUpload(event) {
    event.preventDefault();

    // Validate form
    const examType = examTypeSelect.value;
    const examYear = examYearInput.value;
    const file = zipFileInput.files[0];

    if (!examType || !examYear || !file) {
        showAlert('Please fill all required fields', 'error');
        return;
    }

    // Validate file type
    if (!file.name.toLowerCase().endsWith('.zip')) {
        showAlert('Please select a ZIP file', 'error');
        return;
    }

    // Validate file size (500 MB)
    const maxSize = 500 * 1024 * 1024;
    if (file.size > maxSize) {
        showAlert('File size exceeds 500 MB limit', 'error');
        return;
    }

    // Prepare UI
    progressSection.classList.remove('hidden');
    uploadBtn.disabled = true;
    const progressBar = document.getElementById('progressBar');
    const progressText = document.getElementById('progressText');

    progressBar.style.width = '0%';
    progressBar.textContent = '0%';
    progressText.textContent = 'Starting upload...';

    // Prepare form data
    const formData = new FormData();
    formData.append('file', file);
    formData.append('exam_type', examType);
    formData.append('exam_year', examYear);

    // Use XMLHttpRequest for progress tracking
    const xhr = new XMLHttpRequest();

    // Track upload progress
    xhr.upload.onprogress = function (e) {
        if (e.lengthComputable) {
            const percentComplete = Math.round((e.loaded / e.total) * 100);
            progressBar.style.width = percentComplete + '%';
            progressBar.textContent = percentComplete + '%';

            if (percentComplete < 100) {
                progressText.textContent = `Uploading: ${percentComplete}%`;
            } else {
                progressText.textContent = 'Processing files on server... This may take a few minutes.';
                progressBar.classList.add('progress-bar-striped'); // Optional styling class can be added
            }
        }
    };

    // Handle response
    xhr.onload = function () {
        // Hide progress
        progressSection.classList.add('hidden');
        uploadBtn.disabled = false;

        if (xhr.status === 200) {
            try {
                const data = JSON.parse(xhr.responseText);
                if (data.success) {
                    // Task completed successfully
                    // We need to check if we are in the polling phase or initial upload phase
                    // The initial upload returns success=true directly
                    // polling returns success=true but data is inside task.result

                    let result = data;
                    if (data.task && data.task.result) {
                        result = data.task.result;
                    }

                    showAlert(
                        `✅ Success! Processed ${result.inserted} papers out of ${result.total_pdfs} PDFs found.`,
                        'success'
                    );

                    // Show detailed info
                    if (result.valid_papers !== result.inserted) {
                        showAlert(
                            `ℹ️ Note: ${result.valid_papers} valid engineering papers found, ${result.inserted} successfully inserted into database.`,
                            'info'
                        );
                    }

                    // Reset form
                    uploadForm.reset();
                    fileNameDisplay.textContent = 'Click to select ZIP file';

                    // Set default year
                    const currentYear = new Date().getFullYear();
                    examYearInput.value = currentYear;

                    progressBar.style.width = '0%';
                } else {
                    showAlert(`❌ Error: ${data.error}`, 'error');
                }
            } catch (e) {
                showAlert('❌ Error parsing server response.', 'error');
                console.error('JSON Parse Error:', e);
            }
        } else {
            showAlert(`❌ Server Error: ${xhr.status} ${xhr.statusText}`, 'error');
        }
    };

    // Handle errors
    xhr.onerror = function () {
        progressSection.classList.add('hidden');
        uploadBtn.disabled = false;
        showAlert('❌ Network Error. Please check your connection.', 'error');
    };

    // Open and send request
    xhr.open('POST', `${API_BASE_URL}/admin/upload`, true);
    xhr.send(formData);
}

// Show alert message
function showAlert(message, type = 'info') {
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.innerHTML = message;

    alertContainer.appendChild(alert);

    // Scroll to alert
    alert.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

    // Auto-hide after 10 seconds
    setTimeout(() => {
        alert.remove();
    }, 10000);
}
