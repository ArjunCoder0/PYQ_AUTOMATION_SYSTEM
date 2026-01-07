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

    // Show progress
    progressSection.classList.remove('hidden');
    uploadBtn.disabled = true;

    // Prepare form data
    const formData = new FormData();
    formData.append('file', file);
    formData.append('exam_type', examType);
    formData.append('exam_year', examYear);

    try {
        const response = await fetch(`${API_BASE_URL}/admin/upload`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        // Hide progress
        progressSection.classList.add('hidden');
        uploadBtn.disabled = false;

        if (data.success) {
            showAlert(
                `✅ Success! Processed ${data.inserted} papers out of ${data.total_pdfs} PDFs found.`,
                'success'
            );

            // Show detailed info
            if (data.valid_papers !== data.inserted) {
                showAlert(
                    `ℹ️ Note: ${data.valid_papers} valid engineering papers found, ${data.inserted} successfully inserted into database.`,
                    'info'
                );
            }

            // Reset form
            uploadForm.reset();
            fileNameDisplay.textContent = 'Click to select ZIP file';
            setDefaultYear();
        } else {
            showAlert(`❌ Error: ${data.error}`, 'error');
        }
    } catch (error) {
        progressSection.classList.add('hidden');
        uploadBtn.disabled = false;
        showAlert('❌ Error connecting to server. Please check if the backend is running.', 'error');
        console.error('Upload error:', error);
    }
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
