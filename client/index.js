document.addEventListener('DOMContentLoaded', setupFormHandlers);

function setupFormHandlers() {
    document.getElementById('department-form')?.addEventListener('submit', handleDepartmentSubmit);
    document.getElementById('teacher-form')?.addEventListener('submit', handleTeacherSubmit);
    document.getElementById('subject-form')?.addEventListener('submit', handleSubjectSubmit);
    document.getElementById('room-form')?.addEventListener('submit', handleRoomSubmit);
    document.getElementById('generate-form')?.addEventListener('submit', handleGenerateTimetable);
    document.getElementById('import-timetable-btn')?.addEventListener('click', importTimetable);
}

// Toast notifications
function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `fixed bottom-4 right-4 p-4 rounded shadow-lg ${
        type === 'success' ? 'bg-green-500' : 'bg-red-500'
    } text-white`;
    toast.textContent = message;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}

// Import timetable function
async function importTimetable() {
    const departmentId = document.getElementById('import-department').value;
    const jsonData = document.getElementById('import-json').value;
    
    if (!departmentId) {
        showToast('Please select a department', 'error');
        return;
    }
    
    if (!jsonData) {
        showToast('Please enter timetable JSON data', 'error');
        return;
    }
    
    try {
        const timetableData = JSON.parse(jsonData);
        const response = await fetch('/api/timetables/import', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                department_id: departmentId,
                timetable: timetableData
            })
        });

        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.message || 'Failed to import timetable');
        }

        showToast('Timetable imported successfully', 'success');
        document.getElementById('import-json').value = '';
        await window.appCore.refreshTimetables();
        
    } catch (error) {
        console.error('Error importing timetable:', error);
        showToast(`Error importing timetable: ${error.message}`, 'error');
    }
}

// Form submission handlers
async function handleDepartmentSubmit(event) {
    event.preventDefault();
    
    const departmentData = {
        name: document.getElementById('department-name').value,
        academic_year: document.getElementById('academic-year').value,
        num_branches: parseInt(document.getElementById('num-branches').value) || 1
    };
    
    if (!departmentData.name) {
        showToast('Department name is required!', 'error');
        return;
    }
    
    try {
        const response = await fetch('/api/departments', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(departmentData)
        });
        
        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.message || 'Failed to add department');
        }
        
        document.getElementById('department-form').reset();
        showToast('Department added successfully!', 'success');
        await window.appCore.refreshDepartments();
        
    } catch (error) {
        console.error('Error adding department:', error);
        showToast(`Error adding department: ${error.message}`, 'error');
    }
}

async function handleTeacherSubmit(event) {
    event.preventDefault();
    
    const teacherData = {
        code: document.getElementById('teacher-code').value,
        name: document.getElementById('teacher-name').value,
        specialization: document.getElementById('teacher-specialization').value
    };
    
    if (!teacherData.code || !teacherData.name) {
        showToast('Teacher code and name are required!', 'error');
        return;
    }
    
    try {
        const response = await fetch('/api/teachers', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(teacherData)
        });
        
        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.message || 'Failed to add teacher');
        }
        
        document.getElementById('teacher-form').reset();
        showToast('Teacher added successfully!', 'success');
        await window.appCore.refreshTeachers();
        
    } catch (error) {
        console.error('Error adding teacher:', error);
        showToast(`Error adding teacher: ${error.message}`, 'error');
    }
}

async function handleSubjectSubmit(event) {
    event.preventDefault();
    
    const departmentSelect = document.getElementById('subject-department');
    const yearSelect = document.getElementById('subject-year');
    const departmentId = departmentSelect.value;
    const departmentName = departmentSelect.options[departmentSelect.selectedIndex].text;
    const year = yearSelect.value;
    
    const subjectData = {
        code: document.getElementById('subject-code').value,
        name: document.getElementById('subject-name').value,
        department_id: departmentId,
        department_name: departmentName,
        type: document.getElementById('subject-type').value,
        year: year
    };
    
    if (!subjectData.code || !subjectData.name || !subjectData.department_id || !subjectData.year) {
        showToast('Subject code, name, department, and year are required!', 'error');
        return;
    }
    
    try {
        const response = await fetch('/api/subjects', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(subjectData)
        });
        
        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.message || 'Failed to add subject');
        }
        
        document.getElementById('subject-form').reset();
        showToast('Subject added successfully!', 'success');
        await window.appCore.refreshSubjects();
        
    } catch (error) {
        console.error('Error adding subject:', error);
        showToast(`Error adding subject: ${error.message}`, 'error');
    }
}

async function handleRoomSubmit(event) {
    event.preventDefault();
    
    const roomData = {
        number: document.getElementById('room-number').value,
        capacity: parseInt(document.getElementById('room-capacity').value),
        type: document.getElementById('room-type').value
    };
    
    if (!roomData.number) {
        showToast('Room number is required!', 'error');
        return;
    }
    
    try {
        const response = await fetch('/api/rooms', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(roomData)
        });
        
        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.message || 'Failed to add room');
        }
        
        document.getElementById('room-form').reset();
        showToast('Room added successfully!', 'success');
        await window.appCore.refreshRooms();
        
    } catch (error) {
        console.error('Error adding room:', error);
        showToast(`Error adding room: ${error.message}`, 'error');
    }
}

async function handleGenerateTimetable(event) {
    event.preventDefault();
    
    const departmentId = document.getElementById('timetable-department').value;
    const academicYear = document.getElementById('timetable-academic-year').value;
    
    if (!departmentId || !academicYear) {
        showToast('Department and academic year are required!', 'error');
        return;
    }
    
    const generationStatus = document.getElementById('generation-status');
    const generationSuccess = document.getElementById('generation-success');
    const generationError = document.getElementById('generation-error');
    
    [generationStatus, generationSuccess, generationError].forEach(el => el.classList.add('hidden'));
    generationStatus.classList.remove('hidden');
    
    try {
        generationStatus.textContent = 'Generating timetables for all years (SE, TE, BE), please wait...';
        
        const response = await fetch('/api/generate-timetable', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                department_id: departmentId,
                academic_year: academicYear,
                generate_all_years: true
            })
        });
        
        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.message || 'Failed to generate timetable');
        }
        
        document.getElementById('generate-form').reset();
        generationStatus.classList.add('hidden');
        generationSuccess.classList.remove('hidden');
        generationSuccess.textContent = 'Timetables for all years (SE, TE, BE) generated successfully!';
        showToast('Timetables for all years generated successfully!', 'success');
        
        await window.appCore.refreshTimetables();
        
        setTimeout(() => {
            window.ui.showSection('view');
        }, 1500);
        
    } catch (error) {
        console.error('Error generating timetable:', error);
        generationStatus.classList.add('hidden');
        generationError.classList.remove('hidden');
        generationError.textContent = `Error: ${error.message}`;
        showToast(`Error generating timetable: ${error.message}`, 'error');
    }
}