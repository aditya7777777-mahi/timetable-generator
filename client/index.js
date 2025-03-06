document.addEventListener('DOMContentLoaded', function() {
    // Navigation handling
    const navButtons = document.querySelectorAll('.nav-btn');
    const sections = document.querySelectorAll('.section');
    
    navButtons.forEach(button => {
        button.addEventListener('click', () => {
            // Update active nav button styling
            navButtons.forEach(btn => {
                btn.classList.remove('bg-blue-500', 'text-white');
                btn.classList.add('bg-gray-200', 'hover:bg-gray-300');
            });
            button.classList.remove('bg-gray-200', 'hover:bg-gray-300');
            button.classList.add('bg-blue-500', 'text-white');
            
            // Show the corresponding section
            const sectionId = button.id.replace('nav-', '') + '-section';
            sections.forEach(section => {
                section.classList.add('hidden');
            });
            document.getElementById(sectionId).classList.remove('hidden');
        });
    });
    
    // Load initial data
    showLoadingState();
    Promise.all([
        fetchDepartments(),
        fetchTeachers(),
        fetchSubjects(),
        fetchRooms(),
        fetchTimetables()
    ]).finally(() => {
        hideLoadingState();
    });
    
    // Form submissions
    document.getElementById('department-form').addEventListener('submit', handleDepartmentSubmit);
    document.getElementById('teacher-form').addEventListener('submit', handleTeacherSubmit);
    document.getElementById('subject-form').addEventListener('submit', handleSubjectSubmit);
    document.getElementById('room-form').addEventListener('submit', handleRoomSubmit);
    document.getElementById('generate-form').addEventListener('submit', handleGenerateTimetable);
    
    // Filter timetables by department
    document.getElementById('timetable-select').addEventListener('change', function() {
        const selectedId = this.value;
        if (selectedId) {
            viewTimetable(selectedId);
        }
    });

    // Add timetable tab handlers
    document.querySelectorAll('#timetable-tabs button').forEach(button => {
        button.addEventListener('click', () => {
            // Update active tab styling
            document.querySelectorAll('#timetable-tabs button').forEach(btn => {
                btn.classList.remove('text-blue-600', 'border-blue-600');
                btn.classList.add('hover:text-gray-600', 'hover:border-gray-300');
            });
            button.classList.remove('hover:text-gray-600', 'hover:border-gray-300');
            button.classList.add('text-blue-600', 'border-blue-600');
            
            // Show corresponding content
            const tabType = button.id.replace('tab-', '');
            document.querySelectorAll('.timetable-content').forEach(content => {
                content.classList.add('hidden');
            });
            document.getElementById(`timetable-${tabType}`).classList.remove('hidden');
        });
    });
});

// Loading state functions
function showLoadingState() {
    const loadingEl = document.createElement('div');
    loadingEl.id = 'loading-indicator';
    loadingEl.classList.add('fixed', 'bottom-4', 'right-4', 'bg-blue-500', 'text-white', 'px-4', 'py-2', 'rounded', 'shadow');
    loadingEl.textContent = 'Loading data...';
    document.body.appendChild(loadingEl);
}

function hideLoadingState() {
    const loadingEl = document.getElementById('loading-indicator');
    if (loadingEl) {
        loadingEl.remove();
    }
}

function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.classList.add('fixed', 'bottom-4', 'right-4', 'px-4', 'py-2', 'rounded', 'shadow', 'z-50');
    
    if (type === 'success') {
        toast.classList.add('bg-green-500', 'text-white');
    } else if (type === 'error') {
        toast.classList.add('bg-red-500', 'text-white');
    } else {
        toast.classList.add('bg-blue-500', 'text-white');
    }
    
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 3000);
}

// API Functions
async function fetchDepartments() {
    try {
        const response = await fetch('/api/departments');
        if (!response.ok) {
            throw new Error('Failed to fetch departments');
        }
        
        const departments = await response.json();
        
        // Update departments list
        const departmentsList = document.getElementById('departments-list');
        if (departments.length === 0) {
            departmentsList.innerHTML = '<div class="text-gray-500 italic">No departments added yet</div>';
        } else {
            departmentsList.innerHTML = '';
            departments.forEach(dept => {
                const item = document.createElement('div');
                item.classList.add('py-2', 'border-b', 'last:border-0', 'flex', 'justify-between', 'items-start');
                item.innerHTML = `
                    <div>
                        <div><strong>${dept.name}</strong></div>
                        <div class="text-sm text-gray-600">Academic Year: ${dept.academic_year || 'N/A'}</div>
                        <div class="text-sm text-gray-600">Branches: ${dept.num_branches || 1}</div>
                    </div>
                    <button class="delete-btn bg-red-500 text-white px-2 py-1 rounded hover:bg-red-600 text-sm" data-id="${dept._id}">
                        Delete
                    </button>
                `;
                
                // Add delete event listener
                const deleteBtn = item.querySelector('.delete-btn');
                deleteBtn.addEventListener('click', async (e) => {
                    e.stopPropagation();
                    if (confirm('Are you sure you want to delete this department?')) {
                        try {
                            const response = await fetch(`/api/departments/${dept._id}`, {
                                method: 'DELETE'
                            });
                            
                            if (!response.ok) {
                                throw new Error('Failed to delete department');
                            }
                            
                            showToast('Department deleted successfully', 'success');
                            fetchDepartments(); // Refresh the list
                        } catch (error) {
                            console.error('Error deleting department:', error);
                            showToast(`Error deleting department: ${error.message}`, 'error');
                        }
                    }
                });
                
                departmentsList.appendChild(item);
            });
        }
        
        // Update select dropdowns
        updateDepartmentDropdowns(departments);
        return departments;
        
    } catch (error) {
        console.error('Error fetching departments:', error);
        showToast(`Error fetching departments: ${error.message}`, 'error');
        return [];
    }
}

async function fetchTeachers() {
    try {
        const response = await fetch('/api/teachers');
        if (!response.ok) {
            throw new Error('Failed to fetch teachers');
        }
        
        const teachers = await response.json();
        
        // Update teachers list
        const teachersList = document.getElementById('teachers-list');
        if (!teachersList) {
            console.error('Teachers list element not found');
            return [];
        }

        if (teachers.length === 0) {
            teachersList.innerHTML = '<div class="text-gray-500 italic">No teachers added yet</div>';
        } else {
            teachersList.innerHTML = '';
            teachers.forEach(teacher => {
                const item = document.createElement('div');
                item.classList.add('py-2', 'border-b', 'last:border-0', 'flex', 'justify-between', 'items-start');
                item.innerHTML = `
                    <div>
                        <div><strong>${teacher.code}</strong> - ${teacher.name}</div>
                        <div class="text-sm text-gray-600">Specialization: ${teacher.specialization || 'N/A'}</div>
                    </div>
                    <button class="delete-btn bg-red-500 text-white px-2 py-1 rounded hover:bg-red-600 text-sm" data-id="${teacher._id}">
                        Delete
                    </button>
                `;
                
                // Add delete event listener
                const deleteBtn = item.querySelector('.delete-btn');
                deleteBtn.addEventListener('click', async (e) => {
                    e.stopPropagation();
                    if (confirm('Are you sure you want to delete this teacher?')) {
                        try {
                            const response = await fetch(`/api/teachers/${teacher._id}`, {
                                method: 'DELETE'
                            });
                            
                            if (!response.ok) {
                                throw new Error('Failed to delete teacher');
                            }
                            
                            showToast('Teacher deleted successfully', 'success');
                            fetchTeachers(); // Refresh the list
                        } catch (error) {
                            console.error('Error deleting teacher:', error);
                            showToast(`Error deleting teacher: ${error.message}`, 'error');
                        }
                    }
                });
                
                teachersList.appendChild(item);
            });
        }
        return teachers;
        
    } catch (error) {
        console.error('Error fetching teachers:', error);
        showToast(`Error fetching teachers: ${error.message}`, 'error');
        return [];
    }
}

async function fetchSubjects() {
    try {
        const response = await fetch('/api/subjects');
        if (!response.ok) {
            throw new Error('Failed to fetch subjects');
        }
        
        const subjects = await response.json();
        
        // Get departments for name lookup
        const departmentsResponse = await fetch('/api/departments');
        const departments = await departmentsResponse.json();
        
        // Create a lookup map for department names
        const departmentMap = {};
        departments.forEach(dept => {
            departmentMap[dept._id] = dept.name;
        });
        
        // Update subjects list
        const subjectsList = document.getElementById('subjects-list');
        if (subjects.length === 0) {
            subjectsList.innerHTML = '<div class="text-gray-500 italic">No subjects added yet</div>';
        } else {
            subjectsList.innerHTML = '';
            subjects.forEach(subject => {
                const item = document.createElement('div');
                item.classList.add('py-2', 'border-b', 'last:border-0', 'flex', 'justify-between', 'items-start');
                item.innerHTML = `
                    <div>
                        <div><strong>${subject.code}</strong> - ${subject.name}</div>
                        <div class="text-sm text-gray-600">Type: ${subject.type || 'lecture'}</div>
                        <div class="text-sm text-gray-600">Department: ${departmentMap[subject.department_id] || 'N/A'}</div>
                    </div>
                    <button class="delete-btn bg-red-500 text-white px-2 py-1 rounded hover:bg-red-600 text-sm" data-id="${subject._id}">
                        Delete
                    </button>
                `;
                
                // Add delete event listener
                const deleteBtn = item.querySelector('.delete-btn');
                deleteBtn.addEventListener('click', async (e) => {
                    e.stopPropagation();
                    if (confirm('Are you sure you want to delete this subject?')) {
                        try {
                            const response = await fetch(`/api/subjects/${subject._id}`, {
                                method: 'DELETE'
                            });
                            
                            if (!response.ok) {
                                throw new Error('Failed to delete subject');
                            }
                            
                            showToast('Subject deleted successfully', 'success');
                            fetchSubjects(); // Refresh the list
                        } catch (error) {
                            console.error('Error deleting subject:', error);
                            showToast(`Error deleting subject: ${error.message}`, 'error');
                        }
                    }
                });
                
                subjectsList.appendChild(item);
            });
        }
        return subjects;
        
    } catch (error) {
        console.error('Error fetching subjects:', error);
        showToast(`Error fetching subjects: ${error.message}`, 'error');
        return [];
    }
}

async function fetchRooms() {
    try {
        const response = await fetch('/api/rooms');
        if (!response.ok) {
            throw new Error('Failed to fetch rooms');
        }
        
        const rooms = await response.json();
        
        // Update rooms list
        const roomsList = document.getElementById('rooms-list');
        if (rooms.length === 0) {
            roomsList.innerHTML = '<div class="text-gray-500 italic">No rooms added yet</div>';
        } else {
            roomsList.innerHTML = '';
            rooms.forEach(room => {
                const item = document.createElement('div');
                item.classList.add('py-2', 'border-b', 'last:border-0');
                item.innerHTML = `
                    <div><strong>${room.number}</strong></div>
                    <div class="text-sm text-gray-600">Capacity: ${room.capacity || 'N/A'}</div>
                    <div class="text-sm text-gray-600">Type: ${room.type || 'classroom'}</div>
                `;
                roomsList.appendChild(item);
            });
        }
        return rooms;
        
    } catch (error) {
        console.error('Error fetching rooms:', error);
        showToast(`Error fetching rooms: ${error.message}`, 'error');
        return [];
    }
}

async function fetchTimetables(departmentId = '') {
    try {
        showLoadingState();
        const url = departmentId ? `/api/timetables?department_id=${departmentId}` : '/api/timetables';
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error('Failed to fetch timetables');
        }
        
        const timetables = await response.json();
        
        // Update timetables list
        const timetablesList = document.getElementById('timetables-list');
        if (timetables.length === 0) {
            timetablesList.innerHTML = '<div class="text-gray-500 italic">No timetables generated yet</div>';
        } else {
            timetablesList.innerHTML = '';
            timetables.forEach(timetable => {
                const item = document.createElement('div');
                item.classList.add('py-2', 'border-b', 'last:border-0', 'cursor-pointer', 'hover:bg-gray-100');
                item.innerHTML = `
                    <div>Timetable for ${timetable.academic_year || 'Unknown Academic Year'}</div>
                    <div class="text-sm text-gray-600">Department ID: ${timetable.department_id || 'N/A'}</div>
                    <div class="text-sm text-gray-600">Created: ${formatDate(timetable._id)}</div>
                `;
                item.dataset.id = timetable._id;
                item.addEventListener('click', () => viewTimetable(timetable._id));
                timetablesList.appendChild(item);
            });
        }
        
        return timetables;
        
    } catch (error) {
        console.error('Error fetching timetables:', error);
        showToast(`Error fetching timetables: ${error.message}`, 'error');
        return [];
    } finally {
        hideLoadingState();
    }
}

// Helper function to format dates from MongoDB ObjectId
function formatDate(objectId) {
    try {
        // MongoDB ObjectId's first 4 bytes represent a timestamp in seconds
        const timestamp = parseInt(objectId.substring(0, 8), 16) * 1000;
        return new Date(timestamp).toLocaleDateString();
    } catch (e) {
        return 'Unknown date';
    }
}

async function viewTimetable(timetableId) {
    try {
        showLoadingState();
        const response = await fetch(`/api/timetables/${timetableId}`);
        if (!response.ok) {
            throw new Error('Failed to fetch timetable details');
        }
        
        const timetableData = await response.json();
        
        // Show timetable tabs and content
        document.querySelectorAll('.timetable-content').forEach(el => {
            el.classList.add('hidden');
        });
        document.getElementById('timetable-class').classList.remove('hidden');
        
        // Render timetables for each view
        renderTimetable(timetableData.timetable, 'class');
        renderTimetable(timetableData.timetable_b1 || {}, 'b1');
        renderTimetable(timetableData.timetable_b2 || {}, 'b2');
        renderTimetable(timetableData.timetable_b3 || {}, 'b3');
        
    } catch (error) {
        console.error('Error viewing timetable:', error);
        showToast(`Error viewing timetable: ${error.message}`, 'error');
    } finally {
        hideLoadingState();
    }
}

function renderTimetable(timetableData, type = 'class') {
    const timetableDisplay = document.getElementById(`timetable-display-${type}`);
    if (!timetableDisplay) {
        console.error(`Timetable display element not found for type: ${type}`);
        return;
    }
    
    // Check if there is timetable data
    if (!timetableData || Object.keys(timetableData).length === 0) {
        timetableDisplay.innerHTML = '<div class="text-gray-500 italic">No timetable data available</div>';
        return;
    }
    
    let html = `
        <table class="min-w-full border border-gray-300 mb-8">
            <thead>
                <tr>
                    <th class="border border-gray-300 bg-gray-100 px-4 py-2">Day/Time</th>
    `;
    
    // Add time slots to header
    const days = Object.keys(timetableData);
    const timeSlots = Object.keys(timetableData[days[0]] || {});
    
    timeSlots.forEach(slot => {
        html += `<th class="border border-gray-300 bg-gray-100 px-4 py-2">${slot}</th>`;
    });
    
    html += `</tr></thead><tbody>`;
    
    // Add rows for each day
    days.forEach(day => {
        html += `
            <tr>
                <td class="border border-gray-300 font-semibold px-4 py-2">${day}</td>
        `;
        
        timeSlots.forEach(slot => {
            const cellData = timetableData[day][slot];
            
            if (cellData && cellData.subject) {
                html += `
                    <td class="border border-gray-300 px-4 py-2 timetable-cell">
                        <div class="font-semibold">${cellData.subject}</div>
                        <div class="text-sm text-gray-600">${cellData.teacher || 'No teacher'}</div>
                        <div class="text-sm text-gray-600">${cellData.room || 'No room'}</div>
                        <div class="text-sm text-gray-600">${cellData.type || 'lecture'}</div>
                    </td>
                `;
            } else {
                html += `<td class="border border-gray-300 px-4 py-2 timetable-cell">-</td>`;
            }
        });
        
        html += `</tr>`;
    });
    
    html += `</tbody></table>`;
    timetableDisplay.innerHTML = html;
}

function updateDepartmentDropdowns(departments) {
    const subjectDeptDropdown = document.getElementById('subject-department');
    const timetableDeptDropdown = document.getElementById('timetable-department');
    
    // Clear existing options
    subjectDeptDropdown.innerHTML = '<option value="">Select Department</option>';
    timetableDeptDropdown.innerHTML = '<option value="">Select Department</option>';
    
    // Add departments to dropdowns
    departments.forEach(dept => {
        const option1 = document.createElement('option');
        option1.value = dept._id;
        option1.textContent = dept.name;
        subjectDeptDropdown.appendChild(option1);
        
        const option2 = document.createElement('option');
        option2.value = dept._id;
        option2.textContent = dept.name;
        timetableDeptDropdown.appendChild(option2);
    });
}

// Form Handlers
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
        showLoadingState();
        const response = await fetch('/api/departments', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(departmentData)
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.message || 'Failed to add department');
        }
        
        // Clear form
        document.getElementById('department-form').reset();
        
        // Show success message
        showToast('Department added successfully!', 'success');
        
        // Refresh departments list
        fetchDepartments();
        
    } catch (error) {
        console.error('Error adding department:', error);
        showToast(`Error adding department: ${error.message}`, 'error');
    } finally {
        hideLoadingState();
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
        showLoadingState();
        const response = await fetch('/api/teachers', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(teacherData)
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.message || 'Failed to add teacher');
        }
        
        // Clear form
        document.getElementById('teacher-form').reset();
        
        // Show success message
        showToast('Teacher added successfully!', 'success');
        
        // Refresh teachers list
        fetchTeachers();
        
    } catch (error) {
        console.error('Error adding teacher:', error);
        showToast(`Error adding teacher: ${error.message}`, 'error');
    } finally {
        hideLoadingState();
    }
}

async function handleSubjectSubmit(event) {
    event.preventDefault();
    
    const departmentSelect = document.getElementById('subject-department');
    const departmentId = departmentSelect.value;
    const departmentName = departmentSelect.options[departmentSelect.selectedIndex].text;
    
    // Log for debugging purposes
    console.log(`Adding subject to department: ${departmentName} (ID: ${departmentId})`);
    
    const subjectData = {
        code: document.getElementById('subject-code').value,
        name: document.getElementById('subject-name').value,
        department_id: departmentId,
        department_name: departmentName, // Store name for easier reference
        type: document.getElementById('subject-type').value
    };
    
    if (!subjectData.code || !subjectData.name || !subjectData.department_id) {
        showToast('Subject code, name, and department are required!', 'error');
        return;
    }
    
    try {
        showLoadingState();
        const response = await fetch('/api/subjects', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(subjectData)
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.message || 'Failed to add subject');
        }
        
        // Clear form
        document.getElementById('subject-form').reset();
        
        // Show success message
        showToast('Subject added successfully!', 'success');
        
        // Refresh subjects list
        fetchSubjects();
        
    } catch (error) {
        console.error('Error adding subject:', error);
        showToast(`Error adding subject: ${error.message}`, 'error');
    } finally {
        hideLoadingState();
    }
}

async function handleRoomSubmit(event) {
    event.preventDefault();
    
    const roomData = {
        number: document.getElementById('room-number').value,
        capacity: parseInt(document.getElementById('room-capacity').value) || 0,
        type: document.getElementById('room-type').value
    };
    
    if (!roomData.number) {
        showToast('Room number is required!', 'error');
        return;
    }
    
    try {
        showLoadingState();
        const response = await fetch('/api/rooms', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(roomData)
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.message || 'Failed to add room');
        }
        
        // Clear form
        document.getElementById('room-form').reset();
        
        // Show success message
        showToast('Room added successfully!', 'success');
        
        // Refresh rooms list
        fetchRooms();
        
    } catch (error) {
        console.error('Error adding room:', error);
        showToast(`Error adding room: ${error.message}`, 'error');
    } finally {
        hideLoadingState();
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
    
    // Reset status displays
    [generationStatus, generationSuccess, generationError].forEach(el => el.classList.add('hidden'));
    generationStatus.classList.remove('hidden');
    
    const timetableData = {
        department_id: departmentId,
        academic_year: academicYear
    };
    
    try {
        showLoadingState();
        const response = await fetch('/api/generate-timetable', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(timetableData)
        });
        
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.message || 'Failed to generate timetable');
        }
        
        // Clear form
        document.getElementById('generate-form').reset();
        
        // Show success message
        generationStatus.classList.add('hidden');
        generationSuccess.classList.remove('hidden');
        showToast('Timetable generated successfully!', 'success');
        
        // Refresh timetables list
        await fetchTimetables();
        
        // Switch to view timetables section after a short delay
        setTimeout(() => {
            document.getElementById('nav-view').click();
        }, 1500);
        
    } catch (error) {
        console.error('Error generating timetable:', error);
        
        // Show error message
        generationStatus.classList.add('hidden');
        generationError.classList.remove('hidden');
        generationError.textContent = `Error: ${error.message}`;
        showToast(`Error generating timetable: ${error.message}`, 'error');
    } finally {
        hideLoadingState();
    }
}