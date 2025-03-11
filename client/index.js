document.addEventListener('DOMContentLoaded', initializeApp);

function initializeApp() {
    setupNavigation();
    setupYearTabListeners();
    setupFormListeners();
    initViewSection();
    initImportSection();
    showSection('departments');
}

function setupNavigation() {
    const navButtons = document.querySelectorAll('.nav-btn');
    const sections = document.querySelectorAll('.section');

    navButtons.forEach(button => {
        button.addEventListener('click', () => {
            updateNavButtonStyles(navButtons, button);
            showSection(button.id.replace('nav-', ''));
        });
    });
}

function updateNavButtonStyles(navButtons, activeButton) {
    navButtons.forEach(btn => {
        btn.classList.remove('bg-blue-500', 'text-white');
        btn.classList.add('bg-gray-200', 'hover:bg-gray-300');
    });
    activeButton.classList.remove('bg-gray-200', 'hover:bg-gray-300');
    activeButton.classList.add('bg-blue-500', 'text-white');
}

function setupYearTabListeners() {
    document.getElementById('se-year-tab').addEventListener('click', () => window.timetableRenderer.activateYearTab('SE'));
    document.getElementById('te-year-tab').addEventListener('click', () => window.timetableRenderer.activateYearTab('TE'));
    document.getElementById('be-year-tab').addEventListener('click', () => window.timetableRenderer.activateYearTab('BE'));
}

function setupFormListeners() {
    document.getElementById('department-form').addEventListener('submit', handleDepartmentSubmit);
    document.getElementById('teacher-form').addEventListener('submit', handleTeacherSubmit);
    document.getElementById('subject-form').addEventListener('submit', handleSubjectSubmit);
    document.getElementById('room-form').addEventListener('submit', handleRoomSubmit);
    document.getElementById('generate-form').addEventListener('submit', handleGenerateTimetable);
}

function showSection(sectionId) {
    const sections = document.querySelectorAll('.section');
    sections.forEach(section => section.classList.add('hidden'));
    document.getElementById(`${sectionId}-section`).classList.remove('hidden');
    updateNavButtonStyles(document.querySelectorAll('.nav-btn'), document.getElementById(`nav-${sectionId}`));
}

function initViewSection() {
    loadTimetables();
    document.getElementById('timetable-select').addEventListener('change', function() {
        if (this.value) {
            fetchFormattedTimetable(this.value);
        } else {
            clearTimetableView();
        }
    });
}

function clearTimetableView() {
    document.getElementById('timetable-view').innerHTML = '';
    document.getElementById('timetable-header').classList.add('hidden');
    document.getElementById('faculty-subject-details').classList.add('hidden');
}

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

// Function to fetch and display formatted timetable
function fetchFormattedTimetable(timetableId) {
    fetch(`/api/timetables/${timetableId}/formatted`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to fetch timetable');
            }
            return response.json();
        })
        .then(data => {
            // Use timetableRenderer module to display the formatted timetable
            window.timetableRenderer.displayFormattedTimetable(data.timetable, data.department);
            // Update the app state
            if (window.appCore) {
                window.appCore.updateTimetable(data.timetable);
            }
        })
        .catch(error => {
            console.error('Error fetching timetable:', error);
        });
}

// Load timetables in the view section
function loadTimetables() {
    fetch('/api/timetables')
        .then(response => response.json())
        .then(timetables => {
            const timetableSelect = document.getElementById('timetable-select');
            // Clear existing options except the first one
            while (timetableSelect.options.length > 1) {
                timetableSelect.remove(1);
            }
            
            // Add timetables to select
            timetables.forEach(timetable => {
                const option = document.createElement('option');
                option.value = timetable._id;
                
                // Get the department name if available
                let deptName = 'Unknown Department';
                if (window.globalDepartments && window.globalDepartments.length) {
                    const dept = window.globalDepartments.find(d => d._id === timetable.department_id);
                    if (dept) {
                        deptName = dept.name;
                    }
                }
                
                option.textContent = `${deptName} - ${timetable.academic_year}`;
                timetableSelect.appendChild(option);
            });
        })
        .catch(error => {
            console.error('Error loading timetables:', error);
        });
}

// Function to initialize import section
function initImportSection() {
    loadDepartmentsForImport();
    
    // Add event listener for import button
    document.getElementById('import-timetable-btn').addEventListener('click', importTimetable);
}

// Function to load departments for the import dropdown
function loadDepartmentsForImport() {
    fetch('/api/departments')
        .then(response => response.json())
        .then(departments => {
            const departmentSelect = document.getElementById('import-department');
            // Clear existing options except the first one
            while (departmentSelect.options.length > 1) {
                departmentSelect.remove(1);
            }
            
            // Add departments to select
            departments.forEach(dept => {
                const option = document.createElement('option');
                option.value = dept._id;
                option.textContent = dept.name;
                departmentSelect.appendChild(option);
            });
        })
        .catch(error => {
            console.error('Error loading departments for import:', error);
        });
}

// Import timetable function
function importTimetable() {
    // Get form data
    const departmentId = document.getElementById('import-department').value;
    const academicYear = document.getElementById('import-academic-year').value;
    const jsonData = document.getElementById('import-json').value;
    
    // Validate input
    if (!departmentId) {
        showImportError('Please select a department');
        return;
    }
    
    if (!academicYear) {
        showImportError('Please enter an academic year');
        return;
    }
    
    if (!jsonData) {
        showImportError('Please enter timetable JSON data');
        return;
    }
    
    // Parse JSON
    let timetableData;
    try {
        timetableData = JSON.parse(jsonData);
    } catch (error) {
        showImportError('Invalid JSON format');
        return;
    }
    
    // Create request data
    const requestData = {
        department_id: departmentId,
        academic_year: academicYear,
        timetable: timetableData
    };
    
    // Send request to API
    fetch('/api/timetables/import', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestData)
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(data => {
                throw new Error(data.message || 'Failed to import timetable');
            });
        }
        return response.json();
    })
    .then(data => {
        showImportSuccess('Timetable imported successfully');
        // Clear form
        document.getElementById('import-json').value = '';
        // Reload timetables list
        loadTimetables();
    })
    .catch(error => {
        console.error('Error importing timetable:', error);
        showImportError(error.message);
    });
}

// Show import success message
function showImportSuccess(message) {
    const resultDiv = document.getElementById('import-result');
    resultDiv.innerHTML = `<div class="p-4 mb-4 bg-green-100 text-green-800 rounded">${message || 'Success!'}</div>`;
    
    // Hide after 3 seconds
    setTimeout(() => {
        resultDiv.innerHTML = '';
    }, 3000);
}

// Show import error message
function showImportError(message) {
    const resultDiv = document.getElementById('import-result');
    resultDiv.innerHTML = `<div class="p-4 mb-4 bg-red-100 text-red-800 rounded">${message || 'An error occurred'}</div>`;
    
    // Hide after 5 seconds
    setTimeout(() => {
        resultDiv.innerHTML = '';
    }, 5000);
}

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
        
        // Store departments globally
        window.globalDepartments = departments;
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
                        <div class="text-sm text-gray-600">Year: ${subject.year || 'Not specified'}</div>
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
        // Check if the element exists before trying to modify it
        if (timetablesList) {
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
        }
        
        // Update timetable select dropdown
        const timetableSelect = document.getElementById('timetable-select');
        if (timetableSelect) {
            // Clear existing options
            timetableSelect.innerHTML = '<option value="">Select a Timetable</option>';
            
            // Add timetables to dropdown
            timetables.forEach(timetable => {
                const option = document.createElement('option');
                option.value = timetable._id;
                
                // Try to get the department name
                let deptName = 'Unknown Department';
                if (window.globalDepartments && window.globalDepartments.length) {
                    const dept = window.globalDepartments.find(d => d._id === timetable.department_id);
                    if (dept) {
                        deptName = dept.name;
                    }
                }
                
                option.textContent = `${deptName} - ${timetable.academic_year || 'Unknown'}`;
                timetableSelect.appendChild(option);
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
        
        if (window.appCore) {
            window.appCore.updateTimetable(timetableData);
        }
        
        // Get the department for displaying
        let department = null;
        if (timetableData.department_id && window.globalDepartments) {
            department = window.globalDepartments.find(d => d._id === timetableData.department_id);
        }
        
        // Use timetableRenderer to display the timetable
        window.timetableRenderer.displayFormattedTimetable(timetableData, department);
        
    } catch (error) {
        console.error('Error viewing timetable:', error);
        showToast(`Error viewing timetable: ${error.message}`, 'error');
    } finally {
        hideLoadingState();
    }
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
    const yearSelect = document.getElementById('subject-year');
    const departmentId = departmentSelect.value;
    const departmentName = departmentSelect.options[departmentSelect.selectedIndex].text;
    const year = yearSelect.value;
    
    const subjectData = {
        code: document.getElementById('subject-code').value,
        name: document.getElementById('subject-name').value,
        department_id: departmentId,
        department_id_str: departmentId,
        department_name: departmentName,
        type: document.getElementById('subject-type').value,
        year: year // Add year information
    };
    
    if (!subjectData.code || !subjectData.name || !subjectData.department_id || !subjectData.year) {
        showToast('Subject code, name, department, and year are required!', 'error');
        return;
    }
    
    try {
        showLoadingState();
        
        // First, verify if the department exists
        const deptCheckResponse = await fetch(`/api/departments/${departmentId}`);
        if (!deptCheckResponse.ok) {
            throw new Error('Selected department does not exist or is invalid');
        }
        
        // Now add the subject
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
        academic_year: academicYear,
        generate_all_years: true // Always generate for all years (SE, TE, BE)
    };
    
    try {
        showLoadingState();
        generationStatus.textContent = 'Generating timetables for all years (SE, TE, BE), please wait...';
        
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
        generationSuccess.textContent = 'Timetables for all years (SE, TE, BE) generated successfully!';
        showToast('Timetables for all years generated successfully!', 'success');
        
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

// Add the missing updateDepartmentDropdowns function
function updateDepartmentDropdowns(departments) {
    // Update global departments variable
    window.globalDepartments = departments;
    
    const subjectDeptDropdown = document.getElementById('subject-department');
    const timetableDeptDropdown = document.getElementById('timetable-department');
    const importDeptDropdown = document.getElementById('import-department');
    
    // Update subject department dropdown
    if (subjectDeptDropdown) {
        // Clear existing options
        subjectDeptDropdown.innerHTML = '<option value="">Select Department</option>';
        
        // Add departments to dropdown
        departments.forEach(dept => {
            const option = document.createElement('option');
            option.value = dept._id;
            option.textContent = dept.name;
            subjectDeptDropdown.appendChild(option);
        });
    }
    
    // Update timetable department dropdown
    if (timetableDeptDropdown) {
        // Clear existing options
        timetableDeptDropdown.innerHTML = '<option value="">Select Department</option>';
        
        // Add departments to dropdown
        departments.forEach(dept => {
            const option = document.createElement('option');
            option.value = dept._id;
            option.textContent = dept.name;
            timetableDeptDropdown.appendChild(option);
        });
    }
    
    // Update import department dropdown if it exists
    if (importDeptDropdown) {
        // Clear existing options
        importDeptDropdown.innerHTML = '<option value="">Select Department</option>';
        
        // Add departments to dropdown
        departments.forEach(dept => {
            const option = document.createElement('option');
            option.value = dept._id;
            option.textContent = dept.name;
            importDeptDropdown.appendChild(option);
        });
    }
}document.addEventListener('DOMContentLoaded', initializeApp);

function initializeApp() {
    setupNavigation();
    setupYearTabListeners();
    setupFormListeners();
    initViewSection();
    initImportSection();
    showSection('departments');
}

function setupNavigation() {
    const navButtons = document.querySelectorAll('.nav-btn');
    const sections = document.querySelectorAll('.section');

    navButtons.forEach(button => {
        button.addEventListener('click', () => {
            updateNavButtonStyles(navButtons, button);
            showSection(button.id.replace('nav-', ''));
        });
    });
}

function updateNavButtonStyles(navButtons, activeButton) {
    navButtons.forEach(btn => {
        btn.classList.remove('bg-blue-500', 'text-white');
        btn.classList.add('bg-gray-200', 'hover:bg-gray-300');
    });
    activeButton.classList.remove('bg-gray-200', 'hover:bg-gray-300');
    activeButton.classList.add('bg-blue-500', 'text-white');
}

function setupYearTabListeners() {
    document.getElementById('se-year-tab').addEventListener('click', () => window.timetableRenderer.activateYearTab('SE'));
    document.getElementById('te-year-tab').addEventListener('click', () => window.timetableRenderer.activateYearTab('TE'));
    document.getElementById('be-year-tab').addEventListener('click', () => window.timetableRenderer.activateYearTab('BE'));
}

function setupFormListeners() {
    document.getElementById('department-form').addEventListener('submit', handleDepartmentSubmit);
    document.getElementById('teacher-form').addEventListener('submit', handleTeacherSubmit);
    document.getElementById('subject-form').addEventListener('submit', handleSubjectSubmit);
    document.getElementById('room-form').addEventListener('submit', handleRoomSubmit);
    document.getElementById('generate-form').addEventListener('submit', handleGenerateTimetable);
}

function showSection(sectionId) {
    const sections = document.querySelectorAll('.section');
    sections.forEach(section => section.classList.add('hidden'));
    document.getElementById(`${sectionId}-section`).classList.remove('hidden');
    updateNavButtonStyles(document.querySelectorAll('.nav-btn'), document.getElementById(`nav-${sectionId}`));
}

function initViewSection() {
    loadTimetables();
    document.getElementById('timetable-select').addEventListener('change', function() {
        if (this.value) {
            fetchFormattedTimetable(this.value);
        } else {
            clearTimetableView();
        }
    });
}

function clearTimetableView() {
    document.getElementById('timetable-view').innerHTML = '';
    document.getElementById('timetable-header').classList.add('hidden');
    document.getElementById('faculty-subject-details').classList.add('hidden');
}

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