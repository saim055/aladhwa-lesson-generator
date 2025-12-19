"""
AI-Powered Lesson Plan Generator for Al Adhwa Private School
Uses Anthropic Claude for actual AI generation
"""

import os
import json
from datetime import datetime
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
import zipfile
from pathlib import Path
import anthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class LessonPlanGenerator:
    def __init__(self):
        self.output_folder = 'output'
        self.template_folder = 'documents'
        os.makedirs(self.output_folder, exist_ok=True)
        os.makedirs(self.template_folder, exist_ok=True)
        
        # Initialize Claude client
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
        self.client = anthropic.Anthropic(api_key=api_key)
    
    def generate_complete_package(self, lesson_data):
        """Generate complete lesson plan package using Claude AI"""
        try:
            print(f"Step 1: Generating AI content for {lesson_data['topic']}...")
            ai_content = self.generate_ai_content_with_claude(lesson_data)
            
            print("Step 2: Creating lesson plan document...")
            lesson_doc = self.create_lesson_plan_document(lesson_data, ai_content)
            
            print("Step 3: Creating worksheets...")
            worksheets = self.create_worksheets(lesson_data, ai_content)
            
            print("Step 4: Creating rubrics...")
            rubrics = self.create_rubrics(lesson_data, ai_content)
            
            print("Step 5: Creating question bank...")
            question_bank = self.create_question_bank(lesson_data, ai_content)
            
            print("Step 6: Creating PowerPoint...")
            ppt_file = self.create_powerpoint(lesson_data, ai_content)
            
            print("Step 7: Packaging files...")
            zip_file = self.package_files(lesson_data, [
                lesson_doc, worksheets, rubrics, question_bank, ppt_file
            ])
            
            return {
                'status': 'success',
                'files': {
                    'lesson_plan': os.path.basename(lesson_doc),
                    'worksheets': os.path.basename(worksheets),
                    'rubrics': os.path.basename(rubrics),
                    'question_bank': os.path.basename(question_bank),
                    'powerpoint': os.path.basename(ppt_file),
                    'package': os.path.basename(zip_file)
                },
                'download_url': f'/api/download/{os.path.basename(zip_file)}'
            }
        
        except Exception as e:
            print(f"Error in generate_complete_package: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def generate_ai_content_with_claude(self, lesson_data):
        """Generate comprehensive lesson content using Claude AI"""
        
        # Create detailed prompt based on lesson data
        prompt = self._create_main_prompt(lesson_data)
        
        try:
            print("Calling Claude AI...")
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",  # Fast and cheap
                max_tokens=4000,
                temperature=0.7,
                system=self._get_system_prompt(),
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Parse the response (assuming JSON format)
            content_text = response.content[0].text
            
            # Try to extract JSON if present
            if "```json" in content_text:
                json_str = content_text.split("```json")[1].split("```")[0].strip()
                content = json.loads(json_str)
            elif "{" in content_text and "}" in content_text:
                # Try to find JSON object
                start = content_text.find("{")
                end = content_text.rfind("}") + 1
                json_str = content_text[start:end]
                content = json.loads(json_str)
            else:
                # If not JSON, parse as structured text
                content = self._parse_structured_response(content_text, lesson_data)
            
            return content
            
        except Exception as e:
            print(f"Claude API error: {e}")
            # Fallback to template generation
            return self._generate_with_templates(lesson_data)
    
    def _get_system_prompt(self):
        """Return the system prompt for Claude"""
        return """You are an expert UAE curriculum designer at Al Adhwa Private School. 
Generate detailed, pedagogically sound lesson plans that:
1. Follow UAE/ADEK curriculum standards
2. Include HOT (Higher Order Thinking) objectives
3. Provide DOK-level differentiated outcomes
4. Integrate UAE values authentically
5. Include specific, actionable activities
6. Provide clear assessment strategies
7. Connect to real-world applications in UAE context

Always output in valid JSON format with the structure requested."""
    
    def _create_main_prompt(self, lesson_data):
        """Create the main prompt for lesson plan generation"""
        return f"""
Generate a complete, detailed lesson plan in JSON format for Al Adhwa Private School.

LESSON DETAILS:
- Grade: {lesson_data['grade']}
- Subject: {lesson_data['subject']}
- Topic: {lesson_data['topic']}
- Period: {lesson_data['period']}
- Date: {lesson_data['date']}
- Semester: {lesson_data['semester']}
- UAE Value: {lesson_data.get('value', 'Respect/Care')}
- Standards: {', '.join(lesson_data.get('standards', [])) if lesson_data.get('standards') else 'Not specified'}
- Digital Platform: {lesson_data.get('digital_platform', 'Not specified')}
- Gifted/Talented: {'Yes' if lesson_data.get('gifted_talented') else 'No'}

REQUIRED JSON STRUCTURE:
{{
  "objectives": "3-4 HOT objectives using Bloom's Taxonomy verbs (analyze, evaluate, create, design). Format: 'Students will be able to [VERB] [specific content] through [method].'",
  
  "differentiated_outcomes": {{
    "assistance": "DOK 1-2 outcomes for struggling learners - focus on recall and basic skills",
    "average": "DOK 2-3 outcomes for average learners - focus on application and analysis",
    "upper": "DOK 3-4 outcomes for advanced learners - focus on evaluation and creation",
    "gifted": "DOK 4 outcomes for gifted learners - focus on synthesis and innovation (if applicable)"
  }},
  
  "vocabulary": ["list", "of", "8-10", "subject-specific", "key", "terms"],
  
  "resources": ["list", "of", "5-7", "specific", "resources", "needed"],
  
  "skills": ["Critical Thinking", "Problem Solving", "Collaboration", "Communication", "Digital Literacy"],
  
  "starter": {{
    "activity": "5-minute engaging starter activity with specific instructions",
    "questions": ["3-4 specific guiding questions for the starter"]
  }},
  
  "teaching_component": {{
    "method": "Specific teaching methodology (10 minutes maximum)",
    "steps": ["Step 1", "Step 2", "Step 3", "Step 4", "Step 5"]
  }},
  
  "cooperative_tasks": {{
    "assistance": {{
      "activity": "DOK 1-2 group activity for struggling learners",
      "questions": ["4-5 specific guiding questions"],
      "vak": "Visual/Auditory/Kinesthetic elements"
    }},
    "average": {{
      "activity": "DOK 2-3 group activity for average learners",
      "questions": ["4-5 specific guiding questions"],
      "vak": "Visual/Auditory/Kinesthetic elements"
    }},
    "upper": {{
      "activity": "DOK 3-4 group activity for advanced learners",
      "questions": ["4-5 specific guiding questions"],
      "vak": "Visual/Auditory/Kinesthetic elements"
    }},
    "gifted": {{
      "activity": "DOK 4 group activity for gifted learners",
      "questions": ["4-5 specific guiding questions"],
      "vak": "Visual/Auditory/Kinesthetic elements"
    }}
  }},
  
  "independent_tasks": {{
    "assistance": {{
      "activity": "DOK 1-2 independent task for struggling learners",
      "questions": ["4-5 specific guiding questions"],
      "vak": "Visual/Auditory/Kinesthetic elements"
    }},
    "average": {{
      "activity": "DOK 2-3 independent task for average learners",
      "questions": ["4-5 specific guiding questions"],
      "vak": "Visual/Auditory/Kinesthetic elements"
    }},
    "upper": {{
      "activity": "DOK 3-4 independent task for advanced learners",
      "questions": ["4-5 specific guiding questions"],
      "vak": "Visual/Auditory/Kinesthetic elements"
    }},
    "gifted": {{
      "activity": "DOK 4 independent task for gifted learners",
      "questions": ["4-5 specific guiding questions"],
      "vak": "Visual/Auditory/Kinesthetic elements"
    }}
  }},
  
  "plenary": {{
    "activity": "5-minute plenary activity to consolidate learning",
    "questions": ["3-4 reflection questions"]
  }},
  
  "world_application": "Specific real-world application, especially in UAE context. 2-3 paragraphs.",
  
  "adek_integration": {{
    "my_identity": "How lesson connects to UAE identity, culture, and national development (2-3 sentences)",
    "moral_education": {{
      "pillar": "Character and Morality / Ethics and Values / Community and Civic Responsibility",
      "connection": "Specific connection to moral education (2-3 sentences)"
    }},
    "steam": {{
      "science": "Science connection",
      "technology": "Technology connection",
      "engineering": "Engineering connection",
      "art": "Art connection",
      "math": "Math connection"
    }},
    "links_to_subjects": "Specific links to other subjects (Mathematics, English, ICT, etc.)",
    "environment": "Connection to sustainability and environmental awareness (2-3 sentences)"
  }}
}}

SPECIFIC REQUIREMENTS:
1. All activities must include SPECIFIC guiding questions (not generic)
2. Differentiation must be CLEAR and PRACTICAL
3. UAE context must be AUTHENTIC (not just mentioned)
4. Include REAL examples and specific instructions
5. Make content GRADE-APPROPRIATE for {lesson_data['grade']}
6. For Period {lesson_data['period']}, focus on: {self._get_period_focus(lesson_data['period'])}

Output ONLY valid JSON, no additional text.
"""
    
    def _get_period_focus(self, period):
        """Return focus based on period number"""
        period_focus = {
            "1": "foundational concepts and introduction",
            "2": "development and application of concepts",
            "3": "mastery and higher-order thinking"
        }
        return period_focus.get(period, "concept development")
    
    def _parse_structured_response(self, text, lesson_data):
        """Parse Claude's text response into structured content"""
        # This is a fallback parser - ideally Claude outputs JSON
        # But we parse text if needed
        return self._generate_with_templates(lesson_data)
    
    def _generate_with_templates(self, lesson_data):
        """Fallback template generation (existing code)"""
        # This is your existing template code - keep as fallback
        content = {
            'objectives': self._generate_objectives(lesson_data),
            'differentiated_outcomes': self._generate_outcomes(lesson_data),
            'vocabulary': self._generate_vocabulary(lesson_data),
            'resources': self._generate_resources(lesson_data),
            'skills': self._generate_skills(lesson_data),
            'starter': self._generate_starter(lesson_data),
            'teaching_component': self._generate_teaching(lesson_data),
            'cooperative_tasks': self._generate_differentiated_tasks(lesson_data, 'cooperative'),
            'independent_tasks': self._generate_differentiated_tasks(lesson_data, 'independent'),
            'plenary': self._generate_plenary(lesson_data),
            'world_application': self._generate_world_application(lesson_data),
            'adek_integration': self._generate_adek_integration(lesson_data)
        }
        return content

# KEEP ALL YOUR EXISTING TEMPLATE FUNCTIONS HERE (as fallback)
# _generate_objectives, _generate_outcomes, etc.
# But rename the current generate_ai_content to _generate_with_templates

# ... [Keep all your existing template functions exactly as they are, 
# but rename generate_ai_content to _generate_with_templates]
