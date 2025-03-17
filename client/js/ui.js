/**
 * UI Module
 * Handles UI interactions and DOM manipulations
 */

const ui = (() => {
    const showSection = (sectionId) => {
        // Update navigation styling
        const navButtons = document.querySelectorAll('.nav-btn');
        navButtons.forEach(btn => {
            btn.classList.remove('bg-blue-500', 'text-white');
            btn.classList.add('bg-gray-200', 'hover:bg-gray-300');
            
            if (btn.id === `nav-${sectionId}`) {
                btn.classList.remove('bg-gray-200', 'hover:bg-gray-300');
                btn.classList.add('bg-blue-500', 'text-white');
            }
        });
        
        // Show/hide sections
        document.querySelectorAll('.section').forEach(section => {
            section.classList.add('hidden');
        });
        document.getElementById(`${sectionId}-section`)?.classList.remove('hidden');
        
        // Load section data
        switch(sectionId) {
            case 'departments':
                displayDepartments();
                break;
            case 'teachers':
                displayTeachers();
                break;
            case 'subjects':
                displaySubjects();
                updateTeacherDropdown(); // Update teacher dropdown when viewing subjects section
                break;
            case 'rooms':
                displayRooms();
                break;
            case 'view':
                loadTimetables();
                break;
        }
    };

    const updateTeacherDropdown = () => {
        const teacherDropdown = document.getElementById('subject-teacher');
        if (!teacherDropdown) return;
        
        // Save current selection
        const currentValue = teacherDropdown.value;
        
        // Clear existing options except the first placeholder
        while (teacherDropdown.options.length > 1) {
            teacherDropdown.remove(1);
        }
        
        // Add teachers to dropdown
        const teachers = window.appCore?.state?.teachers || [];
        teachers.forEach(teacher => {
            const option = document.createElement('option');
            option.value = teacher._id;
            option.textContent = `${teacher.code} - ${teacher.name}`;
            teacherDropdown.appendChild(option);
        });
        
        // Restore selection if possible
        if (currentValue) {
            teacherDropdown.value = currentValue;
        }
    };

    const displayDepartments = () => {
        const departmentsList = document.getElementById('departments-list');
        if (!departmentsList) return;

        departmentsList.innerHTML = '';
        const departments = window.appCore?.state?.departments || [];

        if (departments.length === 0) {
            departmentsList.innerHTML = '<div class="text-gray-500 italic">No departments added yet</div>';
            return;
        }

        departments.forEach(dept => {
            const departmentItem = document.createElement('div');
            departmentItem.className = 'flex justify-between items-center border-b py-2';
            departmentItem.innerHTML = `
                <div>
                    <p class="font-semibold">${dept.name}</p>
                    <p class="text-sm text-gray-600">Academic Year: ${dept.academic_year}</p>
                    <p class="text-sm text-gray-600">Branches: ${dept.num_branches || 'N/A'}</p>
                </div>
                <button class="delete-department text-red-500 hover:text-red-700" data-id="${dept._id}">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M9 2a1 0 00-.894.553L7.382 4H4a1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 0 012 0v6a1 0 11-2 0V8zm5-1a1 0 00-1 1v6a1 0 102 0V8a1 0 00-1-1z" clip-rule="evenodd" />
                    </svg>
                </button>
            `;

            // Add delete handler
            const deleteButton = departmentItem.querySelector('.delete-department');
            deleteButton.addEventListener('click', async () => {
                if (confirm('Are you sure you want to delete this department?')) {
                    try {
                        const response = await fetch(`/api/departments/${dept._id}`, {
                            method: 'DELETE'
                        });
                        
                        if (!response.ok) {
                            throw new Error('Failed to delete department');
                        }
                        
                        showToast('Department deleted successfully');
                        await window.appCore.refreshDepartments();
                        displayDepartments();
                    } catch (error) {
                        console.error('Error deleting department:', error);
                        showToast('Error deleting department', 'error');
                    }
                }
            });

            departmentsList.appendChild(departmentItem);
        });
    };

    const displayTeachers = () => {
        const teachersList = document.getElementById('teachers-list');
        if (!teachersList) return;

        teachersList.innerHTML = '';
        const teachers = window.appCore?.state?.teachers || [];

        if (teachers.length === 0) {
            teachersList.innerHTML = '<div class="text-gray-500 italic">No teachers added yet</div>';
            return;
        }

        teachers.forEach(teacher => {
            const teacherItem = document.createElement('div');
            teacherItem.className = 'flex justify-between items-center border-b py-2';
            teacherItem.innerHTML = `
                <div>
                    <p class="font-semibold">${teacher.code} - ${teacher.name}</p>
                    <p class="text-sm text-gray-600">Specialization: ${teacher.specialization || 'N/A'}</p>
                </div>
                <button class="delete-teacher text-red-500 hover:text-red-700" data-id="${teacher._id}">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M9 2a1 0 00-.894.553L7.382 4H4a1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 0 012 0v6a1 0 11-2 0V8zm5-1a1 0 00-1 1v6a1 0 102 0V8a1 0 00-1-1z" clip-rule="evenodd" />
                    </svg>
                </button>
            `;

            // Add delete handler
            const deleteButton = teacherItem.querySelector('.delete-teacher');
            deleteButton.addEventListener('click', async () => {
                if (confirm('Are you sure you want to delete this teacher?')) {
                    try {
                        const response = await fetch(`/api/teachers/${teacher._id}`, {
                            method: 'DELETE'
                        });
                        
                        if (!response.ok) {
                            throw new Error('Failed to delete teacher');
                        }
                        
                        showToast('Teacher deleted successfully');
                        await window.appCore.refreshTeachers();
                        displayTeachers();
                    } catch (error) {
                        console.error('Error deleting teacher:', error);
                        showToast('Error deleting teacher', 'error');
                    }
                }
            });

            teachersList.appendChild(teacherItem);
        });
    };

    const displaySubjects = () => {
        const subjectsList = document.getElementById('subjects-list');
        if (!subjectsList) return;

        subjectsList.innerHTML = '';
        const subjects = window.appCore?.state?.subjects || [];

        if (subjects.length === 0) {
            subjectsList.innerHTML = '<div class="text-gray-500 italic">No subjects added yet</div>';
            return;
        }

        subjects.forEach(subject => {
            const subjectItem = document.createElement('div');
            subjectItem.className = 'flex justify-between items-center border-b py-2';
            
            // Find department name
            let departmentName = 'Unknown Department';
            if (window.appCore?.state?.departments) {
                const department = window.appCore.state.departments.find(
                    dept => dept._id === subject.department_id
                );
                if (department) {
                    departmentName = department.name;
                }
            }

            // Get teacher info if assigned
            let teacherInfo = '';
            if (subject.teacher_id || subject.teacher_name) {
                const teacherCode = subject.teacher_code || '';
                const teacherName = subject.teacher_name || '';
                teacherInfo = `
                    <p class="text-sm text-gray-600">Teacher: ${teacherCode ? teacherCode + ' - ' : ''}${teacherName}</p>
                `;
            }

            subjectItem.innerHTML = `
                <div>
                    <p class="font-semibold">${subject.code} - ${subject.name}</p>
                    <p class="text-sm text-gray-600">Department: ${departmentName}</p>
                    <p class="text-sm text-gray-600">Year: ${subject.year}, Type: ${subject.type?.charAt(0).toUpperCase() + subject.type?.slice(1) || 'N/A'}</p>
                    ${teacherInfo}
                </div>
                <button class="delete-subject text-red-500 hover:text-red-700" data-id="${subject._id}">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M9 2a1 0 00-.894.553L7.382 4H4a1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 0 012 0v6a1 0 11-2 0V8zm5-1a1 0 00-1 1v6a1 0 102 0V8a1 0 00-1-1z" clip-rule="evenodd" />
                    </svg>
                </button>
            `;

            // Add delete handler
            const deleteButton = subjectItem.querySelector('.delete-subject');
            deleteButton.addEventListener('click', async () => {
                if (confirm('Are you sure you want to delete this subject?')) {
                    try {
                        const response = await fetch(`/api/subjects/${subject._id}`, {
                            method: 'DELETE'
                        });
                        
                        if (!response.ok) {
                            throw new Error('Failed to delete subject');
                        }
                        
                        showToast('Subject deleted successfully');
                        await window.appCore.refreshSubjects();
                        displaySubjects();
                    } catch (error) {
                        console.error('Error deleting subject:', error);
                        showToast('Error deleting subject', 'error');
                    }
                }
            });

            subjectsList.appendChild(subjectItem);
        });
    };

    const displayRooms = () => {
        const roomsList = document.getElementById('rooms-list');
        if (!roomsList) return;

        roomsList.innerHTML = '';
        const rooms = window.appCore?.state?.rooms || [];

        if (rooms.length === 0) {
            roomsList.innerHTML = '<div class="text-gray-500 italic">No rooms added yet</div>';
            return;
        }

        rooms.forEach(room => {
            const roomItem = document.createElement('div');
            roomItem.className = 'flex justify-between items-center border-b py-2';
            roomItem.innerHTML = `
                <div>
                    <p class="font-semibold">${room.number}</p>
                    <p class="text-sm text-gray-600">Capacity: ${room.capacity || 'N/A'}</p>
                    <p class="text-sm text-gray-600">Type: ${room.type || 'classroom'}</p>
                </div>
                <button class="delete-room text-red-500 hover:text-red-700" data-id="${room._id}">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M9 2a1 0 00-.894.553L7.382 4H4a1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 0 012 0v6a1 0 11-2 0V8zm5-1a1 0 00-1 1v6a1 0 102 0V8a1 0 00-1-1z" clip-rule="evenodd" />
                    </svg>
                </button>
            `;

            // Add delete handler
            const deleteButton = roomItem.querySelector('.delete-room');
            deleteButton.addEventListener('click', async () => {
                if (confirm('Are you sure you want to delete this room?')) {
                    try {
                        const response = await fetch(`/api/rooms/${room._id}`, {
                            method: 'DELETE'
                        });
                        
                        if (!response.ok) {
                            throw new Error('Failed to delete room');
                        }
                        
                        showToast('Room deleted successfully');
                        await window.appCore.refreshRooms();
                        displayRooms();
                    } catch (error) {
                        console.error('Error deleting room:', error);
                        showToast('Error deleting room', 'error');
                    }
                }
            });

            roomsList.appendChild(roomItem);
        });
    };

    const loadTimetables = () => {
        const timetableSelect = document.getElementById('timetable-select');
        if (!timetableSelect) return;

        const timetables = window.appCore?.state?.timetables || [];
        
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
            if (window.appCore?.state?.departments) {
                const dept = window.appCore.state.departments.find(d => d._id === timetable.department_id);
                if (dept) {
                    deptName = dept.name;
                }
            }
            
            option.textContent = `${deptName} - ${timetable.academic_year}`;
            timetableSelect.appendChild(option);
        });
    };

    /**
     * Load and display a timetable by ID
     * @param {string} timetableId - ID of the timetable to load
     */
    const loadTimetableById = async (timetableId) => {
        if (!timetableId) return;

        try {
            showLoadingState();
            const timetableData = await window.api.fetchTimetableById(timetableId);
            
            if (!timetableData) {
                showToast('Failed to load timetable data', 'error');
                return;
            }

            // Find the department for this timetable
            let department = null;
            if (window.appCore?.state?.departments && timetableData.department_id) {
                department = window.appCore.state.departments.find(
                    dept => dept._id === timetableData.department_id
                );
            }

            // Update app state with current timetable
            if (window.appCore) {
                window.appCore.updateTimetable(timetableData);
            }

            // Render the timetable
            window.timetableRenderer.displayFormattedTimetable(timetableData, department);
        } catch (error) {
            console.error('Error loading timetable:', error);
            showToast('Error loading timetable', 'error');
        } finally {
            hideLoadingState();
        }
    };

    /**
     * Activate a specific year tab in the timetable view
     * @param {string} year - Year to activate (SE, TE, BE)
     */
    const activateYearTab = (year) => {
        if (window.timetableRenderer) {
            window.timetableRenderer.activateYearTab(year);
        }
    };

    const updateDepartmentDropdowns = (departments) => {
        const dropdowns = [
            'subject-department',
            'timetable-department',
            'import-department'
        ].map(id => document.getElementById(id)).filter(Boolean);

        dropdowns.forEach(dropdown => {
            // Save current selection
            const currentValue = dropdown.value;
            
            // Clear existing options except the first placeholder
            while (dropdown.options.length > 1) {
                dropdown.remove(1);
            }
            
            // Add departments
            departments.forEach(dept => {
                const option = document.createElement('option');
                option.value = dept._id;
                option.textContent = dept.name;
                dropdown.appendChild(option);
            });
            
            // Restore selection if possible
            if (currentValue) {
                dropdown.value = currentValue;
            }
        });
    };

    const showToast = (message, type = 'success') => {
        const toast = document.createElement('div');
        toast.className = `fixed bottom-4 right-4 p-4 rounded shadow-lg ${
            type === 'success' ? 'bg-green-500' : 'bg-red-500'
        } text-white z-50`;
        toast.textContent = message;
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 3000);
    };

    const showLoadingState = () => {
        const loadingOverlay = document.getElementById('loading-overlay');
        if (loadingOverlay) {
            loadingOverlay.classList.remove('hidden');
        }
    };

    const hideLoadingState = () => {
        const loadingOverlay = document.getElementById('loading-overlay');
        if (loadingOverlay) {
            loadingOverlay.classList.add('hidden');
        }
    };

    return {
        init() {
            // Initialize all necessary UI components
            showSection('departments');
            
            // Add event listeners to navigation buttons
            document.querySelectorAll('.nav-btn').forEach(button => {
                button.addEventListener('click', () => {
                    // Extract the section ID from the button ID (e.g., 'nav-departments' -> 'departments')
                    const sectionId = button.id.replace('nav-', '');
                    showSection(sectionId);
                });
            });
            
            // Setup year tab functionality in timetable view
            const yearTabs = document.querySelectorAll('.year-tab');
            yearTabs.forEach(tab => {
                tab.addEventListener('click', () => {
                    // Remove active class from all tabs
                    yearTabs.forEach(t => t.classList.remove('active'));
                    // Add active class to clicked tab
                    tab.classList.add('active');
                    
                    // Handle year tab switching logic
                    const year = tab.getAttribute('data-year');
                    const timetableId = document.getElementById('timetable-select').value;
                    if (timetableId && year) {
                        // Call timetable rendering with selected year
                        if (window.timetableRenderer) {
                            window.timetableRenderer.activateYearTab(year);
                        }
                    }
                });
            });

            // Add event listener for timetable selection
            const timetableSelect = document.getElementById('timetable-select');
            if (timetableSelect) {
                timetableSelect.addEventListener('change', () => {
                    const selectedId = timetableSelect.value;
                    if (selectedId) {
                        loadTimetableById(selectedId);
                    } else {
                        // Clear the timetable view if no timetable is selected
                        document.getElementById('timetable-view').innerHTML = '';
                        document.getElementById('timetable-header').classList.add('hidden');
                        document.getElementById('year-tabs-container').classList.add('hidden');
                        document.getElementById('faculty-subject-details').classList.add('hidden');
                    }
                });
            }
        },
        showSection,
        showToast,
        showLoadingState,
        hideLoadingState,
        updateDepartmentDropdowns,
        updateTeacherDropdown,
        displayDepartments,
        displayTeachers,
        displaySubjects,
        displayRooms,
        loadTimetables,
        activateYearTab,
        loadTimetableById
    };
})();

// Export the UI module
window.ui = ui;
