/**
 * Frontend JavaScript for Admin Panel - Out-of-Band ZIP Ingestion
 * Handles server-side ZIP download from URLs with status polling
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
const downloadProgress = document.getElementById('downloadProgress');
const downloadMessage = document.getElementById('downloadMessage');
const downloadBar = document.getElementById('downloadBar');
const downloadText = document.getElementById('downloadText');
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
let statusPollInterval = null;

// Initialize immediately (script is loaded after DOM is ready)
setupEventListeners();
setDefaultYear();
loadRecentJob(); // Auto-load most recent job if exists

// Load most recent job
async function loadRecentJob() {
    console.log('Attempting to load recent job...');
    try {
        const url = `${API_BASE_URL}/admin/recent-job`;
        console.log('Fetching from:', url);

        const response = await Auth.fetch(url);
        console.log('Response status:', response.status);

        const data = await response.json();
        console.log('Response data:', data);

        if (data.success && data.job) {
            const job = data.job;
            console.log('Job found:', job);

            // Only auto-load if job is not completed
            if (job.status !== 'COMPLETED') {
                console.log('Resuming job...');
                currentJobId = job.id;

                // Hide download section, show processing section
                downloadProgress.classList.add('hidden');
                processingSection.classList.remove('hidden');

                // Set job info
                jobFilename.textContent = job.filename;
                uploadMessage.textContent = `Resuming job: ${job.filename}`;

                // Update progress
                const percentage = job.total_pdfs > 0
                    ? Math.round((job.processed_pdfs / job.total_pdfs) * 100)
                    : 0;
                updateProgress(job.processed_pdfs, job.total_pdfs, percentage);

                addLog(`✓ Resumed job: ${job.filename} (${job.processed_pdfs}/${job.total_pdfs})`);
                showAlert(`Resumed previous job: ${job.filename}`, 'info');
            } else {
                console.log('Job already completed, not resuming');
            }
        } else {
            console.log('No job to resume');
        }
    } catch (error) {
        console.error('Error loading recent job:', error);
    }
}

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
    uploadBtn.textContent = '⏳ Starting download...';
    downloadProgress.classList.remove('hidden');

    try {
        // Call fetch-zip endpoint
        const response = await Auth.fetch(`${API_BASE_URL}/admin/fetch-zip`, {
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
            currentJobId = data.job_id;

            // Show download in progress
            downloadMessage.textContent = 'Server is downloading the ZIP file in the background. Please wait...';
            downloadBar.textContent = 'Downloading...';
            downloadBar.style.width = '50%';
            downloadText.textContent = 'Download in progress (checking status every 5 seconds)';

            // Start polling job status
            startStatusPolling(data.job_id, data.filename);

        } else {
            throw new Error(data.error || 'Download failed');
        }
    } catch (error) {
        showAlert(`Error: ${error.message}`, 'error');
        downloadProgress.classList.add('hidden');
        uploadBtn.disabled = false;
        uploadBtn.textContent = '🔗 Fetch ZIP from Server';
    }
}

// Start polling job status
function startStatusPolling(jobId, filename) {
    let attempts = 0;
    const maxAttempts = 120; // 10 minutes max (5 second intervals)

    statusPollInterval = setInterval(async () => {
        attempts++;

        try {
            const response = await Auth.fetch(`${API_BASE_URL}/admin/job-status/${jobId}`);
            const data = await response.json();

            downloadText.textContent = `Checking status... (${attempts * 5} seconds elapsed)`;

            if (data.status === 'UPLOADED') {
                // Download complete!
                clearInterval(statusPollInterval);

                downloadBar.style.width = '100%';
                downloadBar.textContent = '100%';
                downloadText.textContent = '✓ Download complete!';

                setTimeout(() => {
                    downloadProgress.classList.add('hidden');
                    processingSection.classList.remove('hidden');

                    jobFilename.textContent = filename;
                    uploadMessage.textContent = 'ZIP file downloaded successfully! Ready to process.';
                    updateProgress(0, data.total_pdfs || 1, 0);
                    batchProgressText.textContent = `Ready to process (click button to start)`;
                    addLog(`✓ Downloaded: ${filename}`);

                    uploadBtn.disabled = false;
                    uploadBtn.textContent = '🔗 Fetch ZIP from Server';

                    showAlert('Download complete! Click "Process Next 15 PDFs" to start.', 'success');
                }, 1000);

            } else if (data.status === 'FAILED') {
                clearInterval(statusPollInterval);
                throw new Error('Download failed on server');

            } else if (data.status === 'FETCHING') {
                // Still downloading, continue polling
                if (attempts >= maxAttempts) {
                    clearInterval(statusPollInterval);
                    throw new Error('Download timeout - file may be too large or server is slow');
                }
            }
        } catch (error) {
            clearInterval(statusPollInterval);
            downloadProgress.classList.add('hidden');
            uploadBtn.disabled = false;
            uploadBtn.textContent = '🔗 Fetch ZIP from Server';
            showAlert(`Download error: ${error.message}`, 'error');
        }
    }, 5000); // Check every 5 seconds
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
        const response = await Auth.fetch(`${API_BASE_URL}/admin/process-batch/${currentJobId}`, {
            method: 'POST'
        });

        const data = await response.json();

        if (data.success) {
            updateProgress(data.processed, data.total, data.percentage);

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
            const response = await Auth.fetch(`${API_BASE_URL}/admin/process-batch/${currentJobId}`, {
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
            autoProcessBtn.textContent = '🔄 Auto Process All';
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
