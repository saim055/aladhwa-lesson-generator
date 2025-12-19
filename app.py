"""
Al Adhwa Private School - AI Lesson Plan Generator
Main Flask Application
"""

from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import os
from datetime import datetime
import json
from lesson_generator import LessonPlanGenerator
import traceback

app = Flask(__name__)
CORS(app)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'output'

# Ensure folders exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
os.makedirs('documents', exist_ok=True)

# Initialize lesson plan generator
generator = LessonPlanGenerator()

# Month to Value mapping
MONTH_VALUES = {
    9: "Respect/Care",
    10: "Respect/Integrity",
    11: "Respect/Resilience",
    12: "Respect/Perseverance",
    1: "Honesty/Integrity",
    2: "Honesty/Empathy",
    3: "Honesty/Resilience",
    4: "Tolerance/Perseverance",
    5: "Tolerance/Resilience",
    6: "Tolerance/Care"
}

@app.route('/')
def index():
    """Render main page"""
    return render_template('index.html')

@app.route('/api/get-month-value', methods=['POST'])
def get_month_value():
    """Get value based on selected date"""
    try:
        data = request.json
        date_str = data.get('date')
        
        if not date_str:
            return jsonify({'error': 'Date is required'}), 400
        
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        month = date_obj.month
        
        value = MONTH_VALUES.get(month, "Respect/Care")
        
        return jsonify({
            'value': value,
            'month': month,
            'month_name': date_obj.strftime('%B')
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-lesson-plan', methods=['POST'])
def generate_lesson_plan():
    """Generate complete lesson plan package"""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['date', 'semester', 'grade', 'subject', 'topic', 'period']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Extract form data
        lesson_data = {
            'date': data['date'],
            'semester': data['semester'],
            'grade': data['grade'],
            'subject': data['subject'],
            'topic': data['topic'],
            'period': data['period'],
            'standards': data.get('standards', []),
            'digital_platform': data.get('digital_platform', ''),
            'gifted_talented': data.get('gifted_talented', False),
            'ppt_style': data.get('ppt_style', '7E Model'),
            'value': data.get('value', '')
        }
        
        # Generate lesson plan package
        print(f"Generating lesson plan for: {lesson_data['topic']}")
        result = generator.generate_complete_package(lesson_data)
        
        if result['status'] == 'success':
            return jsonify({
                'status': 'success',
                'message': 'Lesson plan package generated successfully!',
                'files': result['files'],
                'download_url': result['download_url']
            })
        else:
            return jsonify({
                'status': 'error',
                'message': result.get('message', 'Generation failed')
            }), 500
    
    except Exception as e:
        print(f"Error in generate_lesson_plan: {str(e)}")
        print(traceback.format_exc())
        return jsonify({
            'status': 'error',
            'message': f'Server error: {str(e)}'
        }), 500

@app.route('/api/download/<filename>')
def download_file(filename):
    """Download generated file"""
    try:
        file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy', 
        'service': 'Al Adhwa Lesson Plan Generator',
        'folders': {
            'templates': os.path.exists('templates'),
            'static': os.path.exists('static'),
            'output': os.path.exists('output'),
            'documents': os.path.exists('documents')
        }
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)