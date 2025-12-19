// Al Adhwa Lesson Plan Generator - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Get form elements
    const form = document.getElementById('lessonForm');
    const dateInput = document.getElementById('date');
    const valueInput = document.getElementById('value');
    const loadingDiv = document.getElementById('loading');
    const resultDiv = document.getElementById('result');
    const progressText = document.getElementById('progress-text');
    const downloadBtn = document.getElementById('downloadBtn');
    const newPlanBtn = document.getElementById('newPlanBtn');

    // Auto-fill value based on selected date
    dateInput.addEventListener('change', async function() {
        const selectedDate = this.value;
        if (!selectedDate) return;

        try {
            const response = await fetch('/api/get-month-value', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ date: selectedDate })
            });

            const data = await response.json();
            
            if (data.value) {
                valueInput.value = data.value;
            } else if (data.error) {
                console.error('Error fetching month value:', data.error);
            }
        } catch (error) {
            console.error('Error:', error);
        }
    });

    // Handle form submission
    form.addEventListener('submit', async function(e) {
        e.preventDefault();

        // Collect form data
        const formData = new FormData(form);
        const data = {
            date: formData.get('date'),
            semester: formData.get('semester'),
            grade: formData.get('grade'),
            subject: formData.get('subject'),
            topic: formData.get('topic'),
            period: formData.get('period'),
            value: formData.get('value'),
            standards: formData.getAll('standards'),
            digital_platform: formData.get('digital_platform'),
            gifted_talented: formData.get('gifted_talented') === 'on',
            ppt_style: formData.get('ppt_style')
        };

        // Validate required fields
        if (!data.date || !data.semester || !data.grade || !data.subject || !data.topic || !data.period) {
            alert('Please fill in all required fields marked with *');
            return;
        }

        // Show loading state
        form.classList.add('hidden');
        loadingDiv.classList.remove('hidden');
        resultDiv.classList.add('hidden');

        // Progress messages
        const progressSteps = [
            '🔍 Analyzing lesson parameters...',
            '🎯 Generating HOT objectives...',
            '✨ Creating engaging starter activity...',
            '📚 Developing differentiated tasks...',
            '🇦🇪 Integrating UAE/ADEK framework...',
            '📝 Creating worksheets and rubrics...',
            '🎨 Building PowerPoint presentation...',
            '📦 Packaging all files...'
        ];

        let stepIndex = 0;
        const progressInterval = setInterval(() => {
            if (stepIndex < progressSteps.length) {
                progressText.textContent = progressSteps[stepIndex];
                stepIndex++;
            } else {
                progressText.textContent = '⏳ Finalizing your package...';
            }
        }, 15000); // Change message every 15 seconds

        try {
            // Make API request
            const response = await fetch('/api/generate-lesson-plan', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });

            clearInterval(progressInterval);

            const result = await response.json();

            if (response.ok && result.status === 'success') {
                // Show success
                loadingDiv.classList.add('hidden');
                resultDiv.classList.remove('hidden');

                // Set download link
                downloadBtn.href = result.download_url;

                // Scroll to result
                resultDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
            } else {
                // Show error
                throw new Error(result.message || 'Failed to generate lesson plan');
            }
        } catch (error) {
            clearInterval(progressInterval);
            
            // Show error message
            alert('Error generating lesson plan: ' + error.message + '\n\nPlease try again or contact support.');
            
            // Hide loading, show form again
            loadingDiv.classList.add('hidden');
            form.classList.remove('hidden');
            
            console.error('Generation error:', error);
        }
    });

    // Handle "Generate Another" button
    newPlanBtn.addEventListener('click', function() {
        // Hide result
        resultDiv.classList.add('hidden');
        
        // Show form
        form.classList.remove('hidden');
        
        // Reset form
        form.reset();
        valueInput.value = '';
        
        // Scroll to top
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });

    // Set today's date as default
    const today = new Date().toISOString().split('T')[0];
    dateInput.value = today;
    
    // Trigger date change to auto-fill value
    dateInput.dispatchEvent(new Event('change'));
});