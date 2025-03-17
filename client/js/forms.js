/**
 * Forms Module
 * Handles form submissions and validation for all forms in the application
 */

const forms = (() => {
    /**
     * Handle department form submission
     * @param {Event} event - Form submission event
     */
    const handleDepartmentSubmit = (event) => {
        event.preventDefault();
        
        const departmentName = document.getElementById('department-name').value.trim();
        const academicYear = document.getElementById('academic-year').value.trim();
        const numBranches = parseInt(document.getElementById('num-branches').value);
        
        if (!departmentName) {
            window.ui.showToast('Please enter department name', 'error');
            return;
        }
        
        if (!academicYear) {
            window.ui.showToast('Please enter academic year', 'error');
            return;
        }
        
        // Show loading state
        window.ui.showLoadingState();
        
        // Prepare department data
        const departmentData = {
            name: departmentName,
            academic_year: academicYear,
            num_branches: numBranches
        };
        
        // Send request to create department
        window.api.createDepartment(departmentData)
            .then(newDepartment => {
                // Add to departments list
                const departmentsList = document.getElementById('departments-list');
                
                // Clear "no departments" message if it exists
                if (departmentsList.querySelector('.text-gray-500')) {
                    departmentsList.innerHTML = '';
                }
                
                // Create department item
                const departmentItem = document.createElement('div');
                departmentItem.className = 'flex justify-between items-center border-b py-2';
                departmentItem.innerHTML = `
                    <div>
                        <p class="font-semibold">${newDepartment.name}</p>
                        <p class="text-sm text-gray-600">Academic Year: ${newDepartment.academic_year}</p>
                        <p class="text-sm text-gray-600">Branches: ${newDepartment.num_branches}</p>
                    </div>
                    <button class="delete-department text-red-500 hover:text-red-700" data-id="${newDepartment._id}">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                            <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" />
                        </svg>
                    </button>
                `;
                
                // Add delete event listener
                departmentItem.querySelector('.delete-department').addEventListener('click', function() {
                    const departmentId = this.getAttribute('data-id');
                    deleteDepartment(departmentId, departmentItem);
                });
                
                departmentsList.appendChild(departmentItem);
                
                // Add to global state
                if (window.appCore && window.appCore.state) {
                    window.appCore.state.departments.push(newDepartment);
                }
                
                // Update department dropdowns
                window.ui.updateDepartmentDropdowns(window.appCore.state.departments);
                
                // Clear form
                document.getElementById('department-form').reset();
                
                // Show success message
                window.ui.showToast('Department added successfully');
            })
            .catch(error => {
                console.error('Error adding department:', error);
                window.ui.showToast('Error adding department', 'error');
            })
            .finally(() => {
                window.ui.hideLoadingState();
            });
    };

    /**
     * Delete a department
     * @param {string} departmentId - ID of department to delete
     * @param {HTMLElement} departmentItem - DOM element representing the department
     */
    const deleteDepartment = (departmentId, departmentItem) => {
        if (confirm('Are you sure you want to delete this department?')) {
            window.ui.showLoadingState();
            
            window.api.deleteDepartment(departmentId)
                .then(() => {
                    // Remove from DOM
                    departmentItem.remove();
                    
                    // Remove from global state
                    if (window.appCore && window.appCore.state) {
                        window.appCore.state.departments = window.appCore.state.departments.filter(dept => dept._id !== departmentId);
                    }
                    
                    // Update department dropdowns
                    window.ui.updateDepartmentDropdowns(window.appCore.state.departments);
                    
                    // Show empty message if no departments
                    const departmentsList = document.getElementById('departments-list');
                    if (departmentsList.children.length === 0) {
                        departmentsList.innerHTML = '<div class="text-gray-500 italic">No departments added yet</div>';
                    }
                    
                    window.ui.showToast('Department deleted successfully');
                })
                .catch(error => {
                    console.error('Error deleting department:', error);
                    window.ui.showToast('Error deleting department', 'error');
                })
                .finally(() => {
                    window.ui.hideLoadingState();
                });
        }
    };

    /**
     * Handle teacher form submission
     * @param {Event} event - Form submission event
     */
    const handleTeacherSubmit = (event) => {
        event.preventDefault();
        
        const teacherCode = document.getElementById('teacher-code').value.trim();
        const teacherName = document.getElementById('teacher-name').value.trim();
        const specialization = document.getElementById('teacher-specialization').value.trim();
        
        if (!teacherCode) {
            window.ui.showToast('Please enter teacher code', 'error');
            return;
        }
        
        if (!teacherName) {
            window.ui.showToast('Please enter teacher name', 'error');
            return;
        }
        
        // Show loading state
        window.ui.showLoadingState();
        
        // Prepare teacher data
        const teacherData = {
            code: teacherCode,
            name: teacherName,
            specialization: specialization
        };
        
        // Send request to create teacher
        window.api.createTeacher(teacherData)
            .then(newTeacher => {
                // Add to teachers list
                const teachersList = document.getElementById('teachers-list');
                
                // Clear "no teachers" message if it exists
                if (teachersList.querySelector('.text-gray-500')) {
                    teachersList.innerHTML = '';
                }
                
                // Create teacher item
                const teacherItem = document.createElement('div');
                teacherItem.className = 'flex justify-between items-center border-b py-2';
                teacherItem.innerHTML = `
                    <div>
                        <p class="font-semibold">${newTeacher.code} - ${newTeacher.name}</p>
                        <p class="text-sm text-gray-600">Specialization: ${newTeacher.specialization}</p>
                    </div>
                    <button class="delete-teacher text-red-500 hover:text-red-700" data-id="${newTeacher._id}">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                            <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" />
                        </svg>
                    </button>
                `;
                
                // Add delete event listener
                teacherItem.querySelector('.delete-teacher').addEventListener('click', function() {
                    const teacherId = this.getAttribute('data-id');
                    deleteTeacher(teacherId, teacherItem);
                });
                
                teachersList.appendChild(teacherItem);
                
                // Add to global state
                if (window.appCore && window.appCore.state) {
                    window.appCore.state.teachers.push(newTeacher);
                }
                
                // Clear form
                document.getElementById('teacher-form').reset();
                
                // Show success message
                window.ui.showToast('Teacher added successfully');
            })
            .catch(error => {
                console.error('Error adding teacher:', error);
                window.ui.showToast('Error adding teacher', 'error');
            })
            .finally(() => {
                window.ui.hideLoadingState();
            });
    };

    /**
     * Delete a teacher
     * @param {string} teacherId - ID of teacher to delete
     * @param {HTMLElement} teacherItem - DOM element representing the teacher
     */
    const deleteTeacher = (teacherId, teacherItem) => {
        if (confirm('Are you sure you want to delete this teacher?')) {
            window.ui.showLoadingState();
            
            window.api.deleteTeacher(teacherId)
                .then(() => {
                    // Remove from DOM
                    teacherItem.remove();
                    
                    // Remove from global state
                    if (window.appCore && window.appCore.state) {
                        window.appCore.state.teachers = window.appCore.state.teachers.filter(teacher => teacher._id !== teacherId);
                    }
                    
                    // Show empty message if no teachers
                    const teachersList = document.getElementById('teachers-list');
                    if (teachersList.children.length === 0) {
                        teachersList.innerHTML = '<div class="text-gray-500 italic">No teachers added yet</div>';
                    }
                    
                    window.ui.showToast('Teacher deleted successfully');
                })
                .catch(error => {
                    console.error('Error deleting teacher:', error);
                    window.ui.showToast('Error deleting teacher', 'error');
                })
                .finally(() => {
                    window.ui.hideLoadingState();
                });
        }
    };

    /**
     * Handle subject form submission
     * @param {Event} event - Form submission event
     */
    const handleSubjectSubmit = (event) => {
        event.preventDefault();
        
        const subjectCode = document.getElementById('subject-code').value.trim();
        const subjectName = document.getElementById('subject-name').value.trim();
        const departmentId = document.getElementById('subject-department').value;
        const year = document.getElementById('subject-year').value;
        const type = document.getElementById('subject-type').value;
        const teacherId = document.getElementById('subject-teacher').value;
        
        if (!subjectCode) {
            window.ui.showToast('Please enter subject code', 'error');
            return;
        }
        
        if (!subjectName) {
            window.ui.showToast('Please enter subject name', 'error');
            return;
        }
        
        if (!departmentId) {
            window.ui.showToast('Please select a department', 'error');
            return;
        }
        
        if (!year) {
            window.ui.showToast('Please select a year', 'error');
            return;
        }
        
        // Show loading state
        window.ui.showLoadingState();
        
        // Prepare subject data
        const subjectData = {
            code: subjectCode,
            name: subjectName,
            department_id: departmentId,
            year: year,
            type: type
        };
        
        // Add teacher ID if selected
        if (teacherId) {
            subjectData.teacher_id = teacherId;
        }
        
        // Send request to create subject
        window.api.createSubject(subjectData)
            .then(newSubject => {
                // Add to subjects list
                const subjectsList = document.getElementById('subjects-list');
                
                // Clear "no subjects" message if it exists
                if (subjectsList.querySelector('.text-gray-500')) {
                    subjectsList.innerHTML = '';
                }
                
                // Find department name
                let departmentName = 'Unknown Department';
                if (window.appCore && window.appCore.state) {
                    const department = window.appCore.state.departments.find(dept => dept._id === departmentId);
                    if (department) {
                        departmentName = department.name;
                    }
                }
                
                // Get teacher info if assigned
                let teacherInfo = '';
                if (newSubject.teacher_id || newSubject.teacher_name) {
                    const teacherCode = newSubject.teacher_code || '';
                    const teacherName = newSubject.teacher_name || '';
                    teacherInfo = `
                        <p class="text-sm text-gray-600">Teacher: ${teacherCode ? teacherCode + ' - ' : ''}${teacherName}</p>
                    `;
                }
                
                // Create subject item
                const subjectItem = document.createElement('div');
                subjectItem.className = 'flex justify-between items-center border-b py-2';
                subjectItem.innerHTML = `
                    <div>
                        <p class="font-semibold">${newSubject.code} - ${newSubject.name}</p>
                        <p class="text-sm text-gray-600">Department: ${departmentName}</p>
                        <p class="text-sm text-gray-600">Year: ${newSubject.year}, Type: ${newSubject.type.charAt(0).toUpperCase() + newSubject.type.slice(1)}</p>
                        ${teacherInfo}
                    </div>
                    <button class="delete-subject text-red-500 hover:text-red-700" data-id="${newSubject._id}">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                            <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" />
                        </svg>
                    </button>
                `;
                
                // Add delete event listener
                subjectItem.querySelector('.delete-subject').addEventListener('click', function() {
                    const subjectId = this.getAttribute('data-id');
                    deleteSubject(subjectId, subjectItem);
                });
                
                subjectsList.appendChild(subjectItem);
                
                // Add to global state
                if (window.appCore && window.appCore.state) {
                    window.appCore.state.subjects.push(newSubject);
                }
                
                // Clear form
                document.getElementById('subject-form').reset();
                
                // Show success message
                window.ui.showToast('Subject added successfully');
            })
            .catch(error => {
                console.error('Error adding subject:', error);
                window.ui.showToast('Error adding subject', 'error');
            })
            .finally(() => {
                window.ui.hideLoadingState();
            });
    };

    /**
     * Delete a subject
     * @param {string} subjectId - ID of subject to delete
     * @param {HTMLElement} subjectItem - DOM element representing the subject
     */
    const deleteSubject = (subjectId, subjectItem) => {
        if (confirm('Are you sure you want to delete this subject?')) {
            window.ui.showLoadingState();
            
            window.api.deleteSubject(subjectId)
                .then(() => {
                    // Remove from DOM
                    subjectItem.remove();
                    
                    // Remove from global state
                    if (window.appCore && window.appCore.state) {
                        window.appCore.state.subjects = window.appCore.state.subjects.filter(subject => subject._id !== subjectId);
                    }
                    
                    // Show empty message if no subjects
                    const subjectsList = document.getElementById('subjects-list');
                    if (subjectsList.children.length === 0) {
                        subjectsList.innerHTML = '<div class="text-gray-500 italic">No subjects added yet</div>';
                    }
                    
                    window.ui.showToast('Subject deleted successfully');
                })
                .catch(error => {
                    console.error('Error deleting subject:', error);
                    window.ui.showToast('Error deleting subject', 'error');
                })
                .finally(() => {
                    window.ui.hideLoadingState();
                });
        }
    };

    /**
     * Handle room form submission
     * @param {Event} event - Form submission event
     */
    const handleRoomSubmit = (event) => {
        event.preventDefault();
        
        const roomNumber = document.getElementById('room-number').value.trim();
        const roomCapacity = parseInt(document.getElementById('room-capacity').value);
        const roomType = document.getElementById('room-type').value;
        
        if (!roomNumber) {
            window.ui.showToast('Please enter room number', 'error');
            return;
        }
        
        if (isNaN(roomCapacity) || roomCapacity <= 0) {
            window.ui.showToast('Please enter a valid room capacity', 'error');
            return;
        }
        
        // Show loading state
        window.ui.showLoadingState();
        
        // Prepare room data
        const roomData = {
            number: roomNumber,
            capacity: roomCapacity,
            type: roomType
        };
        
        // Send request to create room
        window.api.createRoom(roomData)
            .then(newRoom => {
                // Add to rooms list
                const roomsList = document.getElementById('rooms-list');
                
                // Clear "no rooms" message if it exists
                if (roomsList.querySelector('.text-gray-500')) {
                    roomsList.innerHTML = '';
                }
                
                // Create room item
                const roomItem = document.createElement('div');
                roomItem.className = 'flex justify-between items-center border-b py-2';
                roomItem.innerHTML = `
                    <div>
                        <p class="font-semibold">${newRoom.number}</p>
                        <p class="text-sm text-gray-600">Capacity: ${newRoom.capacity}</p>
                        <p class="text-sm text-gray-600">Type: ${newRoom.type.charAt(0).toUpperCase() + newRoom.type.slice(1)}</p>
                    </div>
                    <button class="delete-room text-red-500 hover:text-red-700" data-id="${newRoom._id}">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                            <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" />
                        </svg>
                    </button>
                `;
                
                // Add delete event listener
                roomItem.querySelector('.delete-room').addEventListener('click', function() {
                    const roomId = this.getAttribute('data-id');
                    deleteRoom(roomId, roomItem);
                });
                
                roomsList.appendChild(roomItem);
                
                // Add to global state
                if (window.appCore && window.appCore.state) {
                    window.appCore.state.rooms.push(newRoom);
                }
                
                // Clear form
                document.getElementById('room-form').reset();
                
                // Show success message
                window.ui.showToast('Room added successfully');
            })
            .catch(error => {
                console.error('Error adding room:', error);
                window.ui.showToast('Error adding room', 'error');
            })
            .finally(() => {
                window.ui.hideLoadingState();
            });
    };

    /**
     * Delete a room
     * @param {string} roomId - ID of room to delete
     * @param {HTMLElement} roomItem - DOM element representing the room
     */
    const deleteRoom = (roomId, roomItem) => {
        if (confirm('Are you sure you want to delete this room?')) {
            window.ui.showLoadingState();
            
            window.api.deleteRoom(roomId)
                .then(() => {
                    // Remove from DOM
                    roomItem.remove();
                    
                    // Remove from global state
                    if (window.appCore && window.appCore.state) {
                        window.appCore.state.rooms = window.appCore.state.rooms.filter(room => room._id !== roomId);
                    }
                    
                    // Show empty message if no rooms
                    const roomsList = document.getElementById('rooms-list');
                    if (roomsList.children.length === 0) {
                        roomsList.innerHTML = '<div class="text-gray-500 italic">No rooms added yet</div>';
                    }
                    
                    window.ui.showToast('Room deleted successfully');
                })
                .catch(error => {
                    console.error('Error deleting room:', error);
                    window.ui.showToast('Error deleting room', 'error');
                })
                .finally(() => {
                    window.ui.hideLoadingState();
                });
        }
    };

    /**
     * Handle generate timetable form submission
     * @param {Event} event - Form submission event
     */
    const handleGenerateTimetable = (event) => {
        event.preventDefault();
        
        const departmentId = document.getElementById('timetable-department').value;
        const academicYear = document.getElementById('timetable-academic-year').value.trim();
        const dayStartTime = document.getElementById('day-start-time').value;
        const dayEndTime = document.getElementById('day-end-time').value;
        
        if (!departmentId) {
            window.ui.showToast('Please select a department', 'error');
            return;
        }
        
        if (!academicYear) {
            window.ui.showToast('Please enter academic year', 'error');
            return;
        }
        
        if (!dayStartTime) {
            window.ui.showToast('Please enter day start time', 'error');
            return;
        }
        
        if (!dayEndTime) {
            window.ui.showToast('Please enter day end time', 'error');
            return;
        }
        
        // Show loading state
        window.ui.showLoadingState();
        
        // Get the department name for display
        let departmentName = 'Selected Department';
        if (window.appCore && window.appCore.state) {
            const department = window.appCore.state.departments.find(dept => dept._id === departmentId);
            if (department) {
                departmentName = department.name;
            }
        }
        
        // Prepare timetable generation data
        const timetableData = {
            department_id: departmentId,
            academic_year: academicYear,
            day_start_time: dayStartTime,
            day_end_time: dayEndTime
        };
        
        // Send request to generate timetable
        window.api.generateTimetable(timetableData)
            .then(result => {
                // Show success message
                window.ui.showToast('Timetable generated successfully');
                
                // Display generated timetable
                const generateResult = document.getElementById('generate-result');
                generateResult.classList.remove('hidden');
                
                // Set the result text
                document.getElementById('generate-result-text').innerHTML = `
                    <p class="mb-2">Successfully generated timetable for <span class="font-semibold">${departmentName}</span>!</p>
                    <p>You can view and export it from the "View Timetables" section.</p>
                `;
                
                // Add to global state
                if (window.appCore && window.appCore.state) {
                    window.appCore.state.timetables.push(result);
                }
                
                // Clear form
                document.getElementById('generate-form').reset();
            })
            .catch(error => {
                console.error('Error generating timetable:', error);
                window.ui.showToast('Error generating timetable', 'error');
                
                // Display error message
                const generateResult = document.getElementById('generate-result');
                generateResult.classList.remove('hidden');
                
                document.getElementById('generate-result-text').innerHTML = `
                    <p class="text-red-500">Failed to generate timetable. Please try again or check the input parameters.</p>
                `;
            })
            .finally(() => {
                window.ui.hideLoadingState();
            });
    };

    /**
     * Initialize form event listeners
     */
    const initFormHandlers = () => {
        document.getElementById('department-form')?.addEventListener('submit', handleDepartmentSubmit);
        document.getElementById('teacher-form')?.addEventListener('submit', handleTeacherSubmit);
        document.getElementById('subject-form')?.addEventListener('submit', handleSubjectSubmit);
        document.getElementById('room-form')?.addEventListener('submit', handleRoomSubmit);
        document.getElementById('generate-form')?.addEventListener('submit', handleGenerateTimetable);
    };

    return {
        init() {
            initFormHandlers();
        },
        handleDepartmentSubmit,
        handleTeacherSubmit,
        handleSubjectSubmit,
        handleRoomSubmit,
        handleGenerateTimetable
    };
})();

// Export the forms module
window.forms = forms;
