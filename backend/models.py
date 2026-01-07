"""
Data models for PYQ Management System
"""

class PYQFile:
    """
    Model representing a Previous Year Question paper file
    """
    def __init__(self, degree, branch, semester, subject_code, subject_name, 
                 exam_type, exam_year, file_path, file_id=None, created_at=None):
        self.id = file_id
        self.degree = degree
        self.branch = branch
        self.semester = semester
        self.subject_code = subject_code
        self.subject_name = subject_name
        self.exam_type = exam_type
        self.exam_year = exam_year
        self.file_path = file_path
        self.created_at = created_at
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'degree': self.degree,
            'branch': self.branch,
            'semester': self.semester,
            'subject_code': self.subject_code,
            'subject_name': self.subject_name,
            'exam_type': self.exam_type,
            'exam_year': self.exam_year,
            'file_path': self.file_path,
            'created_at': self.created_at
        }
    
    @staticmethod
    def from_dict(data):
        """Create model from dictionary"""
        return PYQFile(
            degree=data.get('degree'),
            branch=data.get('branch'),
            semester=data.get('semester'),
            subject_code=data.get('subject_code'),
            subject_name=data.get('subject_name'),
            exam_type=data.get('exam_type'),
            exam_year=data.get('exam_year'),
            file_path=data.get('file_path'),
            file_id=data.get('id'),
            created_at=data.get('created_at')
        )
