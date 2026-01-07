# Engineering PYQ Management System

A complete web application for managing and accessing Previous Year Question Papers (PYQs) for B.Tech and B.E engineering students.

## 🎯 Features

### For Students
- **Simple Filter Flow**: Session → Branch → Semester → Subject
- **Quick Access**: Reach any question paper in under 15 seconds
- **Mobile-Friendly**: Responsive design optimized for all devices
- **View & Download**: Instant PDF viewing and downloading

### For Administrators
- **Bulk Upload**: Upload entire ZIP files containing thousands of PDFs
- **Automatic Processing**: Intelligent filename parsing and filtering
- **Smart Filtering**: Automatically accepts only B.Tech/B.E papers
- **Organized Storage**: PDFs stored in structured folders

## 📋 System Requirements

- Python 3.8 or higher
- Modern web browser (Chrome, Firefox, Safari, Edge)
- 500 MB+ disk space for PDF storage

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Initialize Database

```bash
cd backend
python database.py
```

This will create the SQLite database and required tables.

### 3. Start Backend Server

```bash
cd backend
python app.py
```

The API server will start at `http://localhost:5000`

### 4. Open Frontend

Open `frontend/index.html` in your web browser, or use a simple HTTP server:

```bash
cd frontend
python -m http.server 8000
```

Then visit `http://localhost:8000`

## 📁 Project Structure

```
PYQ_AUTOMATION_SYSTEM/
├── backend/
│   ├── app.py              # Main Flask application
│   ├── config.py           # Configuration settings
│   ├── database.py         # Database operations
│   ├── models.py           # Data models
│   ├── zip_processor.py    # ZIP extraction and parsing
│   ├── requirements.txt    # Python dependencies
│   └── pyq_system.db       # SQLite database (created on init)
├── frontend/
│   ├── index.html          # Student portal
│   ├── admin.html          # Admin panel
│   ├── app.js              # Student portal logic
│   ├── admin.js            # Admin panel logic
│   └── styles.css          # Responsive styles
└── uploads/
    ├── temp/               # Temporary ZIP extraction
    └── pdfs/               # Permanent PDF storage
```

## 🔧 Configuration

Edit `backend/config.py` to customize:

- **Upload folder paths**
- **Maximum file size** (default: 500 MB)
- **Supported branches** (CSE, IT, ME, CE, EE, ECE)
- **Database location**

## 📤 Admin Usage

### 1. Access Admin Panel

Navigate to `admin.html` in your browser.

### 2. Upload ZIP File

1. Select exam type (Summer/Winter)
2. Enter exam year (e.g., 2025)
3. Choose ZIP file (max 500 MB)
4. Click "Upload and Process"

### 3. PDF Filename Requirements

PDFs must follow this naming pattern:

**Required Elements:**
- Degree: `B.Tech` OR `B.E` OR `Model Curriculum`
- Branch: `CSE`, `IT`, `ME`, `CE`, `EE`, `ECE`
- Semester: Roman numerals `I` to `VIII`
- Subject Code: `BSCxxx`, `ESCxxx`, `PCCxxx`, `HSMCxxx`, `MCxxx`

**Example Valid Filenames:**
```
B.Tech_CSE_III_Sem_BSC301_Data_Structures.pdf
B.E._ME_V_Semester_ESC501_Thermodynamics.pdf
Model_Curriculum_IT_VII_PCC701_Machine_Learning.pdf
```

### 4. Processing Results

The system will:
- ✅ Extract all PDFs from ZIP
- ✅ Filter only B.Tech/B.E papers
- ✅ Parse metadata from filenames
- ✅ Store valid papers in database
- ✅ Organize PDFs in structured folders
- ❌ Ignore non-engineering papers
- ❌ Skip invalid filenames

## 👨‍🎓 Student Usage

### 1. Access Student Portal

Navigate to `index.html` in your browser.

### 2. Find Question Paper

Follow the simple 4-step filter:

1. **Select Exam Session** (e.g., Summer 2025)
2. **Select Branch** (e.g., CSE)
3. **Select Semester** (1-8)
4. **Select Subject** (searchable dropdown)

### 3. View or Download

- Click **View PDF** to open in browser
- Click **Download PDF** to save to device

## 🗄️ Database Schema

### Table: `pyq_files`

| Column        | Type    | Description                    |
|---------------|---------|--------------------------------|
| id            | INTEGER | Primary key                    |
| degree        | TEXT    | B.Tech or B.E                  |
| branch        | TEXT    | Engineering branch             |
| semester      | INTEGER | Semester (1-8)                 |
| subject_code  | TEXT    | Subject code (BSCxxx, etc.)    |
| subject_name  | TEXT    | Subject name                   |
| exam_type     | TEXT    | Summer or Winter               |
| exam_year     | INTEGER | Exam year                      |
| file_path     | TEXT    | Relative path to PDF           |
| created_at    | TIMESTAMP | Upload timestamp             |

## 🔌 API Endpoints

### Student Endpoints

- `GET /api/sessions` - Get all exam sessions
- `GET /api/branches?exam_type=<type>&exam_year=<year>` - Get branches
- `GET /api/subjects?exam_type=<type>&exam_year=<year>&branch=<branch>&semester=<sem>` - Get subjects
- `GET /api/paper?exam_type=<type>&exam_year=<year>&branch=<branch>&semester=<sem>&subject_code=<code>` - Get paper details
- `GET /api/pdf/view/<id>` - View PDF
- `GET /api/pdf/download/<id>` - Download PDF

### Admin Endpoints

- `POST /api/admin/upload` - Upload and process ZIP file
  - Form data: `file`, `exam_type`, `exam_year`

## 🎨 Design Features

- **Modern UI**: Vibrant gradients and smooth animations
- **Mobile-First**: Optimized for smartphones and tablets
- **Large Buttons**: Easy touch targets for mobile users
- **Clean Layout**: Minimal distractions, maximum usability
- **Fast Loading**: Lightweight and optimized

## 🔒 Security Notes

For production deployment:

1. Add authentication for admin panel
2. Implement rate limiting
3. Add CSRF protection
4. Use HTTPS
5. Validate file contents (not just extensions)
6. Add user access logs

## 🐛 Troubleshooting

### Backend won't start
- Check Python version: `python --version` (need 3.8+)
- Install dependencies: `pip install -r requirements.txt`
- Check port 5000 is not in use

### Frontend can't connect to backend
- Verify backend is running at `http://localhost:5000`
- Check browser console for CORS errors
- Ensure `Flask-CORS` is installed

### ZIP upload fails
- Check file size (max 500 MB)
- Verify file is actually a ZIP
- Check disk space availability
- Review backend console for errors

### PDFs not appearing
- Verify filename format matches requirements
- Check backend logs for parsing errors
- Ensure PDFs contain required keywords (B.Tech/B.E)

## 📝 License

This project is created for educational purposes as a college submission project.

## 👥 Support

For issues or questions, check the backend console logs for detailed error messages.

---

**Built with ❤️ for Engineering Students**
