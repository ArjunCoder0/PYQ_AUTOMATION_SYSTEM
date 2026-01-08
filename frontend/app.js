/**
 * Frontend JavaScript for Student Portal
 * Handles filter flow and API integration
 */

// Dynamically set API URL based on environment
const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:5000/api'
    : `${window.location.origin}/api`;

// State management
let selectedSession = null;
let selectedBranch = null;
let selectedSemester = null;
let selectedSubject = null;
let currentPaper = null;

// DOM Elements
const sessionSelect = document.getElementById('sessionSelect');
const branchSelect = document.getElementById('branchSelect');
const semesterButtons = document.querySelectorAll('.semester-btn');
const subjectSelect = document.getElementById('subjectSelect');
const searchBtn = document.getElementById('searchBtn');
const resultSection = document.getElementById('resultSection');
const alertContainer = document.getElementById('alertContainer');

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    loadSessions();
    setupEventListeners();
});

// Setup event listeners
function setupEventListeners() {
    sessionSelect.addEventListener('change', handleSessionChange);
    branchSelect.addEventListener('change', handleBranchChange);
    semesterButtons.forEach(btn => {
        btn.addEventListener('click', handleSemesterClick);
    });
    subjectSelect.addEventListener('change', handleSubjectChange);
    searchBtn.addEventListener('click', handleSearch);

    document.getElementById('viewBtn').addEventListener('click', viewPDF);
    document.getElementById('downloadBtn').addEventListener('click', downloadPDF);
}

// Load exam sessions
async function loadSessions() {
    try {
        const response = await fetch(`${API_BASE_URL}/sessions`);
        const data = await response.json();

        if (data.success) {
            sessionSelect.innerHTML = '<option value="">-- Choose Session --</option>';
            data.sessions.forEach(session => {
                const option = document.createElement('option');
                option.value = JSON.stringify({
                    exam_type: session.exam_type,
                    exam_year: session.exam_year
                });
                option.textContent = session.label;
                sessionSelect.appendChild(option);
            });
        } else {
            showAlert('Failed to load sessions', 'error');
        }
    } catch (error) {
        showAlert('Error connecting to server', 'error');
        console.error('Error:', error);
    }
}

// Handle session selection
async function handleSessionChange() {
    const value = sessionSelect.value;

    // Reset subsequent filters
    resetBranchFilter();
    resetSemesterFilter();
    resetSubjectFilter();
    hideResult();

    if (!value) return;

    selectedSession = JSON.parse(value);

    // Load branches for selected session
    try {
        const response = await fetch(
            `${API_BASE_URL}/branches?exam_type=${selectedSession.exam_type}&exam_year=${selectedSession.exam_year}`
        );
        const data = await response.json();

        if (data.success) {
            branchSelect.innerHTML = '<option value="">-- Choose Branch --</option>';
            data.branches.forEach(branch => {
                const option = document.createElement('option');
                option.value = branch;
                option.textContent = branch;
                branchSelect.appendChild(option);
            });
            branchSelect.disabled = false;
        }
    } catch (error) {
        showAlert('Error loading branches', 'error');
        console.error('Error:', error);
    }
}

// Handle branch selection
function handleBranchChange() {
    selectedBranch = branchSelect.value;

    // Reset subsequent filters
    resetSemesterFilter();
    resetSubjectFilter();
    hideResult();

    if (selectedBranch) {
        // Enable semester buttons
        semesterButtons.forEach(btn => btn.disabled = false);
    }
}

// Handle semester selection
function handleSemesterClick(event) {
    const btn = event.target;
    if (btn.disabled) return;

    // Remove active class from all buttons
    semesterButtons.forEach(b => b.classList.remove('active'));

    // Add active class to clicked button
    btn.classList.add('active');
    selectedSemester = btn.dataset.semester;

    // Reset subject filter
    resetSubjectFilter();
    hideResult();

    // Load subjects
    loadSubjects();
}

// Load subjects
async function loadSubjects() {
    try {
        const response = await fetch(
            `${API_BASE_URL}/subjects?exam_type=${selectedSession.exam_type}&exam_year=${selectedSession.exam_year}&branch=${selectedBranch}&semester=${selectedSemester}`
        );
        const data = await response.json();

        if (data.success) {
            subjectSelect.innerHTML = '<option value="">-- Choose Subject --</option>';
            data.subjects.forEach(subject => {
                const option = document.createElement('option');
                option.value = subject.subject_code;
                option.textContent = `${subject.subject_code} - ${subject.subject_name}`;
                subjectSelect.appendChild(option);
            });
            subjectSelect.disabled = false;
        }
    } catch (error) {
        showAlert('Error loading subjects', 'error');
        console.error('Error:', error);
    }
}

// Handle subject selection
function handleSubjectChange() {
    selectedSubject = subjectSelect.value;
    hideResult();

    if (selectedSubject) {
        searchBtn.disabled = false;
    } else {
        searchBtn.disabled = true;
    }
}

// Handle search
async function handleSearch() {
    if (!selectedSession || !selectedBranch || !selectedSemester || !selectedSubject) {
        showAlert('Please complete all filter selections', 'error');
        return;
    }

    try {
        const response = await fetch(
            `${API_BASE_URL}/paper?exam_type=${selectedSession.exam_type}&exam_year=${selectedSession.exam_year}&branch=${selectedBranch}&semester=${selectedSemester}&subject_code=${selectedSubject}`
        );
        const data = await response.json();

        if (data.success && data.paper) {
            currentPaper = data.paper;
            displayResult(data.paper);
        } else {
            showAlert('Question paper not found', 'error');
        }
    } catch (error) {
        showAlert('Error fetching paper details', 'error');
        console.error('Error:', error);
    }
}

// Display result
function displayResult(paper) {
    document.getElementById('resultSubjectName').textContent = paper.subject_name;
    document.getElementById('resultSubjectCode').textContent = paper.subject_code;
    document.getElementById('resultBranch').textContent = paper.branch;
    document.getElementById('resultSemester').textContent = `Semester ${paper.semester}`;
    document.getElementById('resultSession').textContent = `${paper.exam_type} ${paper.exam_year}`;
    document.getElementById('resultDegree').textContent = paper.degree;

    resultSection.classList.remove('hidden');
    resultSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// View PDF
function viewPDF() {
    if (currentPaper) {
        // If file_path is a Cloudinary URL, open it directly
        if (currentPaper.file_path && currentPaper.file_path.startsWith('http')) {
            window.open(currentPaper.file_path, '_blank');
        } else {
            // Fallback to API endpoint for local files
            window.open(`${API_BASE_URL}/pdf/view/${currentPaper.id}`, '_blank');
        }
    }
}

// Download PDF
function downloadPDF() {
    if (currentPaper) {
        // If file_path is a Cloudinary URL, download it directly
        if (currentPaper.file_path && currentPaper.file_path.startsWith('http')) {
            window.location.href = currentPaper.file_path;
        } else {
            // Fallback to API endpoint for local files
            window.location.href = `${API_BASE_URL}/pdf/download/${currentPaper.id}`;
        }
    }
}

// Reset functions
function resetBranchFilter() {
    branchSelect.innerHTML = '<option value="">-- Choose Branch --</option>';
    branchSelect.disabled = true;
    selectedBranch = null;
}

function resetSemesterFilter() {
    semesterButtons.forEach(btn => {
        btn.disabled = true;
        btn.classList.remove('active');
    });
    selectedSemester = null;
}

function resetSubjectFilter() {
    subjectSelect.innerHTML = '<option value="">-- Choose Subject --</option>';
    subjectSelect.disabled = true;
    selectedSubject = null;
    searchBtn.disabled = true;
}

function hideResult() {
    resultSection.classList.add('hidden');
    currentPaper = null;
}

// Show alert message
function showAlert(message, type = 'info') {
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.textContent = message;

    alertContainer.innerHTML = '';
    alertContainer.appendChild(alert);

    // Auto-hide after 5 seconds
    setTimeout(() => {
        alert.remove();
    }, 5000);
}
