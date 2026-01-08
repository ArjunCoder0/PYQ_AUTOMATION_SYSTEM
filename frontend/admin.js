/**
 * Frontend JavaScript for Admin Panel - Out-of-Band ZIP Ingestion
 * Handles server-side ZIP download from URLs and batch processing
 */

// Dynamically set API URL based on environment
const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:5000/api'
    : `${window.location.origin}/api`;

// DOM Elements
const uploadForm = document.getElementById('uploadForm');
const examTypeSelect = document.getElementById('examType');
const examYearInput = document.getElementById('examYear');
const zipUrlInput = document.getElementById('zipUrl');
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
    uploadForm.addEventListener('submit', handleFetchZip);
    processBatchBtn.addEventListener('click', processSingleBatch);
    autoProcessBtn.addEventListener('click', toggleAutoProcess);
}

// Set default year to current year
function setDefaultYear() {
    const currentYear = new Date().getFullYear();
    examYearInput.value = currentYear;
}

// Handle ZIP fetch from URL
async function handleFetchZip(event) {
    event.preventDefault();

    // Get form values
    const examType = examTypeSelect.value;
    const examYear = examYearInput.value;
    const zipUrl = zipUrlInput.value;

    // Validate inputs
    if (!examType || !examYear || !zipUrl) {
        showAlert('Please fill all required fields', 'error');
        return;
    }

    // Validate URL format
    if (!zipUrl.startsWith('http://') && !zipUrl.startsWith('https://')) {
        showAlert('Please enter a valid HTTP/HTTPS URL', 'error');
        return;
    }

    // Prepare UI
    uploadBtn.disabled = true;
    uploadBtn.textContent = '⏳ Downloading from server...';
    progressSection.classList.remove('hidden');

    try {
        // Call fetch-zip endpoint
        const response = await fetch(`${API_BASE_URL}/admin/fetch-zip`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                url: zipUrl,
                exam_type: examType,
                exam_year: examYear
            })
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
            updateProgress(0, data.total_pdfs || 1, 0);
            batchProgressText.textContent = `Ready to process (click button to start)`;

            // Add log
            const sizeInfo = data.file_size_mb ? ` (${data.file_size_mb} MB)` : '';
            addLog(`✓ Downloaded: ${data.filename}${sizeInfo}`);

            showAlert(data.message, 'success');
        } else {
            throw new Error(data.error || 'Download failed');
        }
    } catch (error) {
        showAlert(`Error: ${error.message}`, 'error');
        addLog(`❌ Error: ${error.message}`);
    } finally {
        uploadBtn.disabled = false;
        uploadBtn.textContent = '� Fetch ZIP from Server';
        progressSection.classList.add('hidden');
    }
}

// Process single batch
async function processSingleBatch() {
    if (!currentJobId) {
        showAlert('No job selected', 'error');
        return;
    }

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
        showAlert(`Error: ${error.message}`, 'error');
        addLog(`❌ Error: ${error.message}`);
    } finally {
        processBatchBtn.disabled = false;
        processBatchBtn.textContent = '⚡ Process Next 15 PDFs';
    }
}

// Toggle auto-processing
async function toggleAutoProcess() {
    isAutoProcessing = !isAutoProcessing;

    if (isAutoProcessing) {
        autoProcessBtn.textContent = '⏸ Stop Auto Process';
        autoProcessBtn.classList.add('btn-danger');
        autoProcessBtn.classList.remove('btn-secondary');
        processBatchBtn.disabled = true;

        addLog('🔄 Auto-processing started...');
        await autoProcessLoop();
    } else {
        autoProcessBtn.textContent = '🔄 Auto Process All';
        autoProcessBtn.classList.remove('btn-danger');
        autoProcessBtn.classList.add('btn-secondary');
        processBatchBtn.disabled = false;

        addLog('⏸ Auto-processing stopped');
    }
}

// Auto-process loop
async function autoProcessLoop() {
    while (isAutoProcessing) {
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
                    autoProcessBtn.textContent = '🔄 Auto Process All';
                    autoProcessBtn.classList.remove('btn-danger');
                    autoProcessBtn.classList.add('btn-secondary');
                    processBatchBtn.disabled = true;
                    autoProcessBtn.disabled = true;
                    showAlert('✓ All PDFs processed successfully!', 'success');
                    addLog('✓ Auto-processing complete!');
                    break;
                }
            } else {
                throw new Error(data.error || 'Processing failed');
            }
        } catch (error) {
            isAutoProcessing = false;
            autoProcessBtn.textContent = '� Auto Process All';
            autoProcessBtn.classList.remove('btn-danger');
            autoProcessBtn.classList.add('btn-secondary');
            processBatchBtn.disabled = false;
            showAlert(`Error: ${error.message}`, 'error');
            addLog(`❌ Auto-processing error: ${error.message}`);
            break;
        }

        // Wait 1 second between batches
        await new Promise(resolve => setTimeout(resolve, 1000));
    }
}

// Update progress bar
function updateProgress(processed, total, percentage) {
    batchProgressBar.style.width = `${percentage}%`;
    batchProgressBar.textContent = `${percentage}%`;
    batchProgressText.textContent = `${processed} / ${total} PDFs (${percentage}%)`;
}

// Add log entry
function addLog(message) {
    const timestamp = new Date().toLocaleTimeString();
    const logEntry = document.createElement('div');
    logEntry.textContent = `[${timestamp}] ${message}`;
    processingLog.appendChild(logEntry);
    processingLog.scrollTop = processingLog.scrollHeight;
}

// Show alert
function showAlert(message, type = 'info') {
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.textContent = message;

    alertContainer.innerHTML = '';
    alertContainer.appendChild(alert);

    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        alert.remove();
    }, 5000);
}
