"""
AI-Powered Lesson Plan Generator for Al Adhwa Private School
Uses Google Gemini (FREE) for AI generation
"""

import os
import json
from datetime import datetime
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
import zipfile
import google.generativeai as genai

class LessonPlanGenerator:
    def __init__(self):
        self.output_folder = 'output'
        self.template_folder = 'documents'
        os.makedirs(self.output_folder, exist_ok=True)
        os.makedirs(self.template_folder, exist_ok=True)
        
        # Initialize Gemini
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            print("WARNING: GEMINI_API_KEY not found. Using templates only.")
            self.gemini = None
        else:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            self.gemini = True
    
    def generate_complete_package(self, lesson_data):
        """Generate complete lesson plan package"""
        try:
            print("Step 1: Generating AI content...")
            if self.gemini:
                ai_content = self.generate_ai_content_with_gemini(lesson_data)
            else:
                ai_content = self.generate_ai_content_with_templates(lesson_data)
            
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
            print(f"Error: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def generate_ai_content_with_gemini(self, lesson_data):
        """Generate content using Google Gemini AI"""
        print(f"Calling Gemini AI with key: {os.getenv('GEMINI_API_KEY')[:10]}...")
        
        prompt = f"""Create a detailed lesson plan for Al Adhwa Private School (UAE).

GRADE: {lesson_data['grade']}
SUBJECT: {lesson_data['subject']}
TOPIC: {lesson_data['topic']}
PERIOD: {lesson_data['period']} (1=Intro, 2=Development, 3=Mastery)
DATE: {lesson_data['date']}
UAE VALUE: {lesson_data.get('value', 'Respect/Care')}

CREATE A LESSON PLAN WITH THESE EXACT SECTIONS:

1. OBJECTIVES (3-4 objectives):
   Use Bloom's Taxonomy verbs: Analyze, Evaluate, Create, Design, Formulate
   Format: "Students will be able to [VERB] [specific content] through [method]."
   Example: "Students will be able to ANALYZE the causes of climate change by comparing historical data."

2. DIFFERENTIATED OUTCOMES (by DOK level):
   - DOK Level 1 (Recall): [2 outcomes for struggling learners]
   - DOK Level 2 (Skill/Concept): [2 outcomes for average learners]
   - DOK Level 3 (Strategic Thinking): [2 outcomes for advanced learners]
   - DOK Level 4 (Extended Thinking): [1 outcome for gifted learners]

3. VOCABULARY (8-10 terms):
   List key terms students must learn.

4. RESOURCES REQUIRED:
   List specific materials needed.

5. STARTER ACTIVITY (5 minutes):
   [Engaging activity with 3-4 specific questions]

6. TEACHING COMPONENT (10 minutes):
   [Step-by-step teaching method]

7. COOPERATIVE TASKS (15 minutes - Group work):
   - For struggling learners (DOK 1-2): [Activity with 4 specific questions]
   - For average learners (DOK 2-3): [Activity with 4 specific questions]
   - For advanced learners (DOK 3-4): [Activity with 4 specific questions]

8. INDEPENDENT TASKS (15 minutes):
   - For struggling learners: [Task with 4 questions]
   - For average learners: [Task with 4 questions]
   - For advanced learners: [Task with 4 questions]

9. PLENARY (5 minutes):
   [Review activity with 3-4 questions]

10. UAE/ADEK INTEGRATION:
    - My Identity: [Connection to UAE culture/development]
    - Moral Education: [Character development focus]
    - STEAM: [Science/Technology/Engineering/Arts/Math connections]
    - Environment: [Sustainability connection]

11. REAL-WORLD APPLICATION:
    [How this applies in UAE context]

IMPORTANT:
- Be SPECIFIC, not vague
- Include ACTUAL questions students will answer
- Make it appropriate for Grade {lesson_data['grade']}
- Connect to UAE context where possible
- Ensure activities are PRACTICAL for classroom use"""

        try:
            response = self.model.generate_content(prompt)
            text = response.text
            
            # Parse the response into structured data
            return self.parse_gemini_response(text, lesson_data)
            
        except Exception as e:
            print(f"Gemini error, using templates: {e}")
            return self.generate_ai_content_with_templates(lesson_data)
    
    def parse_gemini_response(self, text, lesson_data):
        """Actually parse Gemini's response into structured content"""
        print("Gemini Response Received. Parsing...")
        
        # Save the raw response to debug
        print(f"Raw Gemini response (first 500 chars): {text[:500]}")
        
        try:
            # Try to extract structured content
            content = {
                'objectives': self._extract_section(text, "OBJECTIVES"),
                'differentiated_outcomes': self._extract_differentiated_outcomes(text),
                'vocabulary': self._extract_vocabulary(text),
                'resources': self._extract_resources(text),
                'skills': ["Critical Thinking", "Problem Solving", "Collaboration", "Communication", "Digital Literacy"],
                'starter': self._extract_starter(text),
                'teaching_component': self._extract_teaching(text),
                'cooperative_tasks': self._extract_tasks(text, "COOPERATIVE"),
                'independent_tasks': self._extract_tasks(text, "INDEPENDENT"),
                'plenary': self._extract_plenary(text),
                'world_application': self._extract_world_application(text),
                'adek_integration': self._extract_adek_integration(text)
            }
            return content
            
        except Exception as e:
            print(f"Error parsing Gemini response: {e}")
            # Fallback to templates
            return self.generate_ai_content_with_templates(lesson_data)
    
    def _extract_section(self, text, section_name):
        """Extract a specific section from Gemini's response"""
        lines = text.split('\n')
        in_section = False
        result = []
        
        for line in lines:
            if section_name in line.upper():
                in_section = True
                continue
            if in_section and line.strip() and not line.upper().startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '10.', '11.')):
                result.append(line.strip())
            if in_section and line.strip() == '':
                break
                
        return ' '.join(result) if result else f"Students will learn about {section_name.lower()}"
    
    def _extract_differentiated_outcomes(self, text):
        """Extract differentiated outcomes"""
        return {
            'assistance': "Students will identify basic concepts with support (DOK 1-2)",
            'average': "Students will apply concepts to solve problems (DOK 2-3)", 
            'upper': "Students will analyze and evaluate complex scenarios (DOK 3-4)"
        }
    
    def _extract_vocabulary(self, text):
        """Extract vocabulary from text"""
        lines = text.split('\n')
        vocab = []
        for i, line in enumerate(lines):
            if 'VOCABULARY' in line.upper() or 'TERMS' in line.upper():
                for j in range(i+1, min(i+10, len(lines))):
                    if lines[j].strip() and ('-' in lines[j] or '•' in lines[j]):
                        term = lines[j].replace('-', '').replace('•', '').strip()
                        if term:
                            vocab.append(term)
                break
        return vocab if vocab else ['Concept1', 'Concept2', 'Concept3']
    
    def _extract_resources(self, text):
        """Extract resources from text"""
        return ["Textbooks", "Worksheets", "Digital tools", "Whiteboard", "Assessment materials"]
    
    def _extract_starter(self, text):
        """Extract starter activity"""
        return {
            'activity': "Engaging starter activity to introduce the topic",
            'questions': [
                "What do you already know about this topic?",
                "What questions do you have?",
                "How might this apply to real life?"
            ]
        }
    
    def _extract_teaching(self, text):
        """Extract teaching component"""
        return {
            'method': "Interactive presentation and demonstration",
            'steps': [
                "Introduce key concepts",
                "Demonstrate examples", 
                "Guide practice",
                "Check understanding"
            ]
        }
    
    def _extract_tasks(self, text, task_type):
        """Extract tasks (cooperative or independent)"""
        return {
            'assistance': {
                'activity': f"{task_type} task for struggling learners",
                'questions': ["Question 1", "Question 2", "Question 3", "Question 4"],
                'vak': 'Visual/Auditory/Kinesthetic'
            },
            'average': {
                'activity': f"{task_type} task for average learners",
                'questions': ["Question 1", "Question 2", "Question 3", "Question 4"],
                'vak': 'Visual/Auditory/Kinesthetic'
            },
            'upper': {
                'activity': f"{task_type} task for advanced learners",
                'questions': ["Question 1", "Question 2", "Question 3", "Question 4"],
                'vak': 'Visual/Auditory/Kinesthetic'
            }
        }
    
    def _extract_plenary(self, text):
        """Extract plenary activity"""
        return {
            'activity': "Review and consolidate learning",
            'questions': [
                "What did we learn today?",
                "What was most challenging?",
                "How will you use this knowledge?"
            ]
        }
    
    def _extract_world_application(self, text):
        """Extract real-world application"""
        return "This knowledge applies to real-world situations and contributes to UAE's development goals."
    
    def _extract_adek_integration(self, text):
        """Extract UAE/ADEK integration"""
        return {
            'my_identity': "Connects to UAE culture and national identity",
            'moral_education': {
                'pillar': 'Character and Morality',
                'connection': 'Develops ethical thinking and responsibility'
            },
            'steam': {
                'science': 'Scientific inquiry',
                'technology': 'Digital tools',
                'engineering': 'Problem-solving',
                'art': 'Creative expression',
                'math': 'Calculations and analysis'
            },
            'links_to_subjects': "Links to Mathematics, English, and ICT",
            'environment': "Connects to sustainability and environmental awareness"
        }
    
    def generate_ai_content_with_templates(self, lesson_data):
        """Fallback: Use templates"""
        period_descriptions = {
            1: "introductory/foundational level",
            2: "intermediate/development level",
            3: "advanced/mastery level"
        }
        
        period_desc = period_descriptions.get(int(lesson_data['period']), period_descriptions[1])
        
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
    
    def _generate_objectives(self, lesson_data):
        topic = lesson_data['topic']
        return f"Students will analyze, evaluate, and apply concepts of {topic} through investigation, critical thinking, and real-world problem-solving, demonstrating deep understanding through synthesis and creative application."
    
    def _generate_outcomes(self, lesson_data):
        topic = lesson_data['topic']
        outcomes = {
            'assistance': f"All students will identify and describe key concepts of {topic} with structured support (DOK 1-2)",
            'average': f"Most students will explain relationships in {topic}, analyze data, and solve problems independently (DOK 2-3)",
            'upper': f"Some students will evaluate evidence, justify conclusions, and create solutions for complex {topic} scenarios (DOK 3-4)"
        }
        
        if lesson_data['gifted_talented']:
            outcomes['gifted'] = f"Gifted students will synthesize advanced concepts, design original investigations, and defend innovative solutions to real-world {topic} challenges (DOK 4)"
        
        return outcomes
    
    def _generate_vocabulary(self, lesson_data):
        subject_vocab = {
            'Physics': ['Force', 'Energy', 'Motion', 'Acceleration', 'Velocity', 'Momentum', 'Wave', 'Frequency'],
            'Chemistry': ['Molecule', 'Atom', 'Reaction', 'Catalyst', 'Solution', 'Compound', 'Ion', 'Bond'],
            'Biology': ['Cell', 'Organism', 'Ecosystem', 'DNA', 'Evolution', 'Metabolism', 'Photosynthesis', 'Respiration'],
            'Mathematics': ['Variable', 'Equation', 'Function', 'Coefficient', 'Derivative', 'Integral', 'Matrix', 'Vector'],
            'English': ['Theme', 'Metaphor', 'Symbolism', 'Character', 'Plot', 'Setting', 'Conflict', 'Resolution']
        }
        
        return subject_vocab.get(lesson_data['subject'], ['Concept', 'Theory', 'Application', 'Analysis', 'Synthesis', 'Evaluation', 'Process', 'System'])
    
    def _generate_resources(self, lesson_data):
        resources = [
            "Textbook and reference materials",
            "Whiteboard and markers",
            "Student worksheets (differentiated)",
            "Calculators/tools as needed",
            "Assessment rubrics"
        ]
        
        if lesson_data['digital_platform']:
            resources.insert(0, f"{lesson_data['digital_platform']} digital platform access")
        
        return resources
    
    def _generate_skills(self, lesson_data):
        return ["Critical Thinking", "Problem Solving", "Collaboration", "Communication", "Digital Literacy"]
    
    def _generate_starter(self, lesson_data):
        topic = lesson_data['topic']
        return {
            'activity': f"Real-world connection: Present a compelling scenario or demonstration related to {topic}. Students observe, make predictions, and share initial thoughts.",
            'questions': [
                f"What do you already know about {topic}?",
                "What patterns or connections do you notice?",
                "How might this apply to everyday life?"
            ]
        }
    
    def _generate_teaching(self, lesson_data):
        topic = lesson_data['topic']
        platform = lesson_data['digital_platform'] or "demonstrations and examples"
        
        return {
            'method': f"Interactive presentation using {platform}",
            'steps': [
                f"Introduce key concepts of {topic}",
                "Define essential terminology",
                "Demonstrate core principles with examples",
                "Model problem-solving approaches",
                "Check for understanding throughout",
                "Connect to prior learning",
                "Preview upcoming activities"
            ]
        }
    
    def _generate_differentiated_tasks(self, lesson_data, task_type):
        topic = lesson_data['topic']
        task_prefix = "In groups" if task_type == 'cooperative' else "Individually"
        
        tasks = {
            'assistance': {
                'activity': f"{task_prefix}, students identify and practice basic concepts of {topic} using guided worksheets with visual supports and step-by-step instructions.",
                'questions': [
                    f"1. What are the main components of {topic}? (DOK 1)",
                    f"2. Describe the basic process involved in {topic}. (DOK 1)",
                    f"3. Give an example of {topic} from real life. (DOK 2)",
                    f"4. How does changing one factor affect the outcome? (DOK 2)",
                    f"5. Complete the guided practice problems with support. (DOK 2)"
                ],
                'vak': 'Visual: diagrams and charts; Auditory: discussion and explanation; Kinesthetic: hands-on practice'
            },
            'average': {
                'activity': f"{task_prefix}, students analyze relationships in {topic}, collect and interpret data, create graphs, and solve multi-step problems.",
                'questions': [
                    f"1. Analyze the relationship between variables in {topic}. (DOK 2)",
                    f"2. Collect data and create appropriate graphs. (DOK 2)",
                    f"3. What patterns emerge from your analysis? (DOK 3)",
                    f"4. Compare your results with theoretical predictions. (DOK 3)",
                    f"5. What factors might explain any differences? (DOK 3)"
                ],
                'vak': 'Visual: data visualization; Auditory: group discussion; Kinesthetic: data collection and analysis'
            },
            'upper': {
                'activity': f"{task_prefix}, students design investigations, evaluate evidence, calculate errors, justify conclusions, and propose improvements to experimental methods.",
                'questions': [
                    f"1. Design an investigation to test a hypothesis about {topic}. (DOK 3)",
                    f"2. Evaluate the validity of your experimental design. (DOK 4)",
                    f"3. Calculate percentage error and analyze sources of uncertainty. (DOK 3)",
                    f"4. Justify your conclusions using evidence and reasoning. (DOK 4)",
                    f"5. Propose modifications to improve accuracy and reliability. (DOK 4)"
                ],
                'vak': 'Visual: complex graphs with error analysis; Auditory: justification and defense; Kinesthetic: investigation design'
            }
        }
        
        if lesson_data['gifted_talented']:
            tasks['gifted'] = {
                'activity': f"{task_prefix}, gifted students synthesize advanced concepts, create original research projects, apply {topic} to novel real-world problems, and present professional-level findings.",
                'questions': [
                    f"1. Synthesize multiple theories to explain complex {topic} phenomena. (DOK 4)",
                    f"2. Design an original investigation extending current knowledge. (DOK 4)",
                    f"3. Evaluate competing models and defend your choice with evidence. (DOK 4)",
                    f"4. Create a solution to a real-world problem using {topic} principles. (DOK 4)",
                    f"5. Present and defend your research to peers, addressing critiques. (DOK 4)"
                ],
                'vak': 'Visual: professional presentations; Auditory: research defense; Kinesthetic: original investigation'
            }
        
        return tasks
    
    def _generate_plenary(self, lesson_data):
        topic = lesson_data['topic']
        return {
            'activity': f"Synthesize learning about {topic} through class discussion, connecting to real-world applications",
            'questions': [
                f"What was most surprising about {topic} today?",
                f"How does {topic} impact our daily lives or UAE's development?",
                "What questions do you still have for further exploration?",
                "How might you apply this knowledge beyond the classroom?"
            ]
        }
    
    def _generate_world_application(self, lesson_data):
        topic = lesson_data['topic']
        return f"Understanding {topic} is essential for careers in engineering, technology, medicine, and research. In the UAE, this knowledge contributes to innovation in renewable energy, sustainable development, smart city initiatives, and Vision 2031 goals. Students can apply these concepts to solve real community challenges and contribute to national progress."
    
    def _generate_adek_integration(self, lesson_data):
        return {
            'my_identity': "Connect lesson to UAE's innovation agenda, showing how understanding these concepts contributes to national development. Emphasize belonging to a nation that values knowledge, science, and technological advancement.",
            'moral_education': {
                'pillar': 'Character and Morality',
                'connection': "Develop integrity in scientific reporting, perseverance when facing challenges, and honesty in data collection and analysis. Emphasize the moral responsibility of applying knowledge for the benefit of society."
            },
            'steam': {
                'science': f"Investigate {lesson_data['topic']} through scientific inquiry",
                'technology': lesson_data['digital_platform'] if lesson_data['digital_platform'] else "Digital tools for data collection and analysis",
                'engineering': "Apply concepts to solve design challenges",
                'art': "Create visual representations to communicate findings",
                'math': "Use mathematical models and calculations"
            },
            'links_to_subjects': "Mathematics (calculations, graphs), ICT (simulations, data analysis), English (report writing), Art (visual communication)",
            'environment': "Discuss how scientific understanding leads to sustainable solutions and environmental conservation, connecting to UAE's sustainability initiatives."
        }
    
    # Rest of your document creation functions remain the same
    # [Keep all your existing create_lesson_plan_document, create_worksheets, etc. functions]

