/**
 * Frontend JavaScript for Admin Panel - Chunked Upload Architecture
 * Handles ZIP file upload and batch processing
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
const processingSection = document.getElementById('processingSection');
const alertContainer = document.getElementById('alertContainer');

// Processing elements
const uploadMessage = document.getElementById('uploadMessage');
const jobFilename = document.getElementById('jobFilename');
const batchProgressBar = document.getElementById('batchProgressBar');
const batchProgressText = document.getElementById('batchProgressText');
const processBatchBtn = document.getElementById('processBatchBtn');
const autoProcessBtn = document.getElementById('autoProcessBtn');
const processingLog = document.getElementById('processingLog');

// State
let currentJobId = null;
let isAutoProcessing = false;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    setDefaultYear();
});

// Setup event listeners
function setupEventListeners() {
    uploadForm.addEventListener('submit', handleUpload);
    zipFileInput.addEventListener('change', handleFileSelect);
    processBatchBtn.addEventListener('click', processSingleBatch);
    autoProcessBtn.addEventListener('click', toggleAutoProcess);
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

    // Prepare UI
    uploadBtn.disabled = true;
    uploadBtn.textContent = '⏳ Uploading...';
    progressSection.classList.remove('hidden');

    try {
        // Prepare form data
        const formData = new FormData();
        formData.append('file', file);
        formData.append('exam_type', examType);
        formData.append('exam_year', examYear);

        // Upload file
        const response = await fetch(`${API_BASE_URL}/admin/upload`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            // Hide upload section, show processing section
            progressSection.classList.add('hidden');
            processingSection.classList.remove('hidden');

            // Set job info
            currentJobId = data.job_id;
            jobFilename.textContent = data.filename;
            uploadMessage.textContent = data.message;

            // Update progress (total will be 0 until first batch)
            const totalText = data.total_pdfs > 0 ? data.total_pdfs : '?';
            updateProgress(0, data.total_pdfs || 1, 0);
            batchProgressText.textContent = `Ready to process (click button to start)`;

            // Add log
            addLog(`✓ Upload complete: ${data.filename}`);

            showAlert(data.message, 'success');
        } else {
            throw new Error(data.error || 'Upload failed');
        }
    } catch (error) {
        showAlert(`Upload failed: ${error.message}`, 'error');
        progressSection.classList.add('hidden');
    } finally {
        uploadBtn.disabled = false;
        uploadBtn.textContent = '📤 Upload and Process';
    }
}

// Process single batch
async function processSingleBatch() {
    if (!currentJobId) return;

    processBatchBtn.disabled = true;
    processBatchBtn.textContent = '⏳ Processing...';

    try {
        const response = await fetch(`${API_BASE_URL}/admin/process-batch/${currentJobId}`, {
            method: 'POST'
        });

        const data = await response.json();

        if (data.success) {
            updateProgress(data.processed, data.total, data.percentage);

            // Update text with actual total after first batch
            const statusText = data.status === 'COMPLETED'
                ? '✓ Complete!'
                : `Processed batch: ${data.batch_processed} PDFs`;
            addLog(statusText + ` (${data.processed}/${data.total})`);

            if (data.status === 'COMPLETED') {
                processBatchBtn.disabled = true;
                autoProcessBtn.disabled = true;
                showAlert('✓ All PDFs processed successfully!', 'success');
                addLog('✓ Processing complete!');
            }
        } else {
            throw new Error(data.error || 'Processing failed');
        }
    } catch (error) {
        showAlert(`Processing failed: ${error.message}`, 'error');
        addLog(`✗ Error: ${error.message}`);
    } finally {
        processBatchBtn.disabled = false;
        processBatchBtn.textContent = '⚡ Process Next 15 PDFs';
    }
}

// Toggle auto-process
async function toggleAutoProcess() {
    if (isAutoProcessing) {
        // Stop auto-processing
        isAutoProcessing = false;
        autoProcessBtn.textContent = '🚀 Auto Process All';
        processBatchBtn.disabled = false;
        addLog('Auto-processing stopped');
    } else {
        // Start auto-processing
        isAutoProcessing = true;
        autoProcessBtn.textContent = '⏸️ Stop Auto Process';
        processBatchBtn.disabled = true;
        addLog('Auto-processing started...');

        await autoProcessAll();
    }
}

// Auto-process all batches
async function autoProcessAll() {
    while (isAutoProcessing && currentJobId) {
        try {
            const response = await fetch(`${API_BASE_URL}/admin/process-batch/${currentJobId}`, {
                method: 'POST'
            });

            const data = await response.json();

            if (data.success) {
                updateProgress(data.processed, data.total, data.percentage);
                addLog(`Batch complete: ${data.processed}/${data.total} PDFs`);

                if (data.status === 'COMPLETED') {
                    isAutoProcessing = false;
                    autoProcessBtn.textContent = '✓ Complete';
                    autoProcessBtn.disabled = true;
                    processBatchBtn.disabled = true;
                    showAlert('✓ All PDFs processed successfully!', 'success');
                    addLog('✓ All processing complete!');
                    break;
                }

                // Wait 1 second between batches
                await new Promise(resolve => setTimeout(resolve, 1000));
            } else {
                throw new Error(data.error || 'Processing failed');
            }
        } catch (error) {
            isAutoProcessing = false;
            autoProcessBtn.textContent = '🚀 Auto Process All';
            processBatchBtn.disabled = false;
            showAlert(`Processing failed: ${error.message}`, 'error');
            addLog(`✗ Error: ${error.message}`);
            break;
        }
    }
}

// Update progress UI
function updateProgress(processed, total, percentage) {
    batchProgressBar.style.width = `${percentage}%`;
    batchProgressBar.textContent = `${percentage}%`;
    batchProgressText.textContent = `${processed} / ${total} papers (${percentage}%)`;
}

// Add log entry
function addLog(message) {
    processingLog.style.display = 'block';
    const timestamp = new Date().toLocaleTimeString();
    const logEntry = document.createElement('div');
    logEntry.textContent = `[${timestamp}] ${message}`;
    logEntry.style.marginBottom = '0.25rem';
    processingLog.appendChild(logEntry);
    processingLog.scrollTop = processingLog.scrollHeight;
}

// Show alert
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.innerHTML = `
        <strong>${type === 'error' ? '❌' : type === 'success' ? '✓' : 'ℹ️'}</strong> ${message}
    `;

    alertContainer.innerHTML = '';
    alertContainer.appendChild(alertDiv);

    // Auto-remove after 5 seconds
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}
