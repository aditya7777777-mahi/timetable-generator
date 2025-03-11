/**
 * UI Module
 * Handles UI interactions and DOM manipulations
 */

const ui = (() => {
    /**
     * Show a section and hide others
     * @param {string} sectionId - ID of section to show (without '-section' suffix)
     */
    const showSection = (sectionId) => {
        // Get all sections
        const sections = document.querySelectorAll('.section');
        
        // Hide all sections
        sections.forEach(section => {
            section.classList.add('hidden');
        });
        
        // Show the selected section
        document.getElementById(`${sectionId}-section`).classList.remove('hidden');
        
        // Update active navigation button
        const navButtons = document.querySelectorAll('.nav-btn');
        navButtons.forEach(btn => {
            btn.classList.remove('bg-blue-500', 'text-white');
            btn.classList.add('bg-gray-200', 'hover:bg-gray-300');
        });
        
        document.getElementById(`nav-${sectionId}`).classList.remove('bg-gray-200', 'hover:bg-gray-300');
        document.getElementById(`nav-${sectionId}`).classList.add('bg-blue-500', 'text-white');
    };

    /**
     * Initialize navigation
     */
    const initNavigation = () => {
        const navButtons = document.querySelectorAll('.nav-btn');
        
        navButtons.forEach(button => {
            const sectionId = button.id.replace('nav-', '');
            button.addEventListener('click', () => showSection(sectionId));
        });
    };

    /**
     * Initialize year tabs
     */
    const initYearTabs = () => {
        document.getElementById('se-year-tab')?.addEventListener('click', () => window.timetableRenderer.activateYearTab('SE'));
        document.getElementById('te-year-tab')?.addEventListener('click', () => window.timetableRenderer.activateYearTab('TE'));
        document.getElementById('be-year-tab')?.addEventListener('click', () => window.timetableRenderer.activateYearTab('BE'));
    };

    /**
     * Display a toast notification
     * @param {string} message - Message to display
     * @param {string} type - Notification type (success, error)
     */
    const showToast = (message, type = 'success') => {
        const toastContainer = document.getElementById('toast-container') || createToastContainer();
        const toast = document.createElement('div');
        
        toast.className = `p-4 mb-3 rounded shadow-md transition-opacity duration-500 ease-in-out ${
            type === 'success' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
        }`;
        toast.textContent = message;
        
        toastContainer.appendChild(toast);
        
        // Remove after 3 seconds
        setTimeout(() => {
            toast.classList.add('opacity-0');
            setTimeout(() => {
                toastContainer.removeChild(toast);
            }, 500);
        }, 3000);
    };

    /**
     * Create a toast container if it doesn't exist
     * @returns {HTMLElement} - Toast container element
     */
    const createToastContainer = () => {
        const container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'fixed top-4 right-4 z-50';
        document.body.appendChild(container);
        return container;
    };

    /**
     * Show loading state with spinner
     */
    const showLoadingState = () => {
        let loadingOverlay = document.getElementById('loading-overlay');
        
        if (!loadingOverlay) {
            loadingOverlay = document.createElement('div');
            loadingOverlay.id = 'loading-overlay';
            loadingOverlay.className = 'fixed inset-0 bg-gray-700 bg-opacity-50 flex items-center justify-center z-50';
            loadingOverlay.innerHTML = `
                <div class="bg-white p-4 rounded-lg shadow-lg text-center">
                    <div class="inline-block animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-500 mb-2"></div>
                    <p>Loading...</p>
                </div>
            `;
            document.body.appendChild(loadingOverlay);
        } else {
            loadingOverlay.classList.remove('hidden');
        }
    };

    /**
     * Hide loading state
     */
    const hideLoadingState = () => {
        const loadingOverlay = document.getElementById('loading-overlay');
        if (loadingOverlay) {
            loadingOverlay.classList.add('hidden');
        }
    };

    /**
     * Update department dropdown options in all select elements
     * @param {Array} departments - List of departments
     */
    const updateDepartmentDropdowns = (departments) => {
        // Update in subject form
        const subjectDeptSelect = document.getElementById('subject-department');
        if (subjectDeptSelect) {
            // Save current selection
            const currentValue = subjectDeptSelect.value;
            
            // Clear existing options except the first placeholder
            while (subjectDeptSelect.options.length > 1) {
                subjectDeptSelect.remove(1);
            }
            
            // Add departments
            departments.forEach(dept => {
                const option = document.createElement('option');
                option.value = dept._id;
                option.textContent = dept.name;
                subjectDeptSelect.appendChild(option);
            });
            
            // Restore selection if possible
            if (currentValue) {
                subjectDeptSelect.value = currentValue;
            }
        }
        
        // Update in generate form
        const generateDeptSelect = document.getElementById('timetable-department');
        if (generateDeptSelect) {
            // Save current selection
            const currentValue = generateDeptSelect.value;
            
            // Clear existing options except the first placeholder
            while (generateDeptSelect.options.length > 1) {
                generateDeptSelect.remove(1);
            }
            
            // Add departments
            departments.forEach(dept => {
                const option = document.createElement('option');
                option.value = dept._id;
                option.textContent = dept.name;
                generateDeptSelect.appendChild(option);
            });
            
            // Restore selection if possible
            if (currentValue) {
                generateDeptSelect.value = currentValue;
            }
        }
        
        // Update in import form
        const importDeptSelect = document.getElementById('import-department');
        if (importDeptSelect) {
            // Save current selection
            const currentValue = importDeptSelect.value;
            
            // Clear existing options except the first placeholder
            while (importDeptSelect.options.length > 1) {
                importDeptSelect.remove(1);
            }
            
            // Add departments
            departments.forEach(dept => {
                const option = document.createElement('option');
                option.value = dept._id;
                option.textContent = dept.name;
                importDeptSelect.appendChild(option);
            });
            
            // Restore selection if possible
            if (currentValue) {
                importDeptSelect.value = currentValue;
            }
        }
    };

    /**
     * Initialize import section
     */
    const initImportSection = () => {
        // Set up file input
        const fileInput = document.getElementById('import-file');
        const fileLabel = document.getElementById('import-file-label');

        if (fileInput && fileLabel) {
            fileInput.addEventListener('change', function() {
                if (this.files.length > 0) {
                    fileLabel.textContent = this.files[0].name;
                } else {
                    fileLabel.textContent = 'Choose a timetable file';
                }
            });
        }

        // Set up import button
        const importButton = document.getElementById('import-timetable-btn');
        if (importButton) {
            importButton.addEventListener('click', importTimetable);
        }
    };

    /**
     * Import a timetable from file
     */
    const importTimetable = () => {
        const departmentId = document.getElementById('import-department').value;
        const fileInput = document.getElementById('import-file');
        
        if (!departmentId) {
            showToast('Please select a department', 'error');
            return;
        }
        
        if (!fileInput.files || fileInput.files.length === 0) {
            showToast('Please select a file to import', 'error');
            return;
        }
        
        const file = fileInput.files[0];
        const reader = new FileReader();
        
        reader.onload = async function(e) {
            try {
                const timetableData = JSON.parse(e.target.result);
                
                // Add department_id to the timetable data
                timetableData.department_id = departmentId;
                
                // Import the timetable
                const response = await window.api.importTimetable(timetableData);
                
                // Show success message
                showImportSuccess('Timetable imported successfully!');
                
                // Reset form
                document.getElementById('import-department').value = '';
                document.getElementById('import-file').value = '';
                document.getElementById('import-file-label').textContent = 'Choose a timetable file';
                
                // Refresh timetables list
                window.api.fetchTimetables().then(timetables => {
                    window.appCore.state.timetables = timetables;
                });
            } catch (error) {
                showImportError('Error importing timetable: ' + (error.message || 'Invalid file format'));
            }
        };
        
        reader.onerror = function() {
            showImportError('Error reading file');
        };
        
        reader.readAsText(file);
    };

    /**
     * Show import success message
     * @param {string} message - Success message
     */
    const showImportSuccess = (message) => {
        const successMsg = document.getElementById('import-success');
        successMsg.textContent = message;
        successMsg.classList.remove('hidden');
        
        // Hide after 3 seconds
        setTimeout(() => {
            successMsg.classList.add('hidden');
        }, 3000);
    };

    /**
     * Show import error message
     * @param {string} message - Error message
     */
    const showImportError = (message) => {
        const errorMsg = document.getElementById('import-error');
        errorMsg.textContent = message;
        errorMsg.classList.remove('hidden');
        
        // Hide after 3 seconds
        setTimeout(() => {
            errorMsg.classList.add('hidden');
        }, 3000);
    };

    /**
     * Initialize view section
     */
    const initViewSection = () => {
        // Load timetables
        loadTimetables();
        
        // Event listener for timetable selection
        document.getElementById('timetable-select')?.addEventListener('change', function() {
            if (this.value) {
                window.api.getFormattedTimetable(this.value)
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
                        showToast('Error loading timetable', 'error');
                    });
            } else {
                // Hide timetable container
                document.getElementById('timetable-view').innerHTML = '';
                document.getElementById('timetable-header').classList.add('hidden');
                document.getElementById('faculty-subject-details').classList.add('hidden');
            }
        });
    };
    
    /**
     * Load timetables in the view section
     */
    const loadTimetables = () => {
        window.api.fetchTimetables()
            .then(timetables => {
                const timetableSelect = document.getElementById('timetable-select');
                if (!timetableSelect) return;
                
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
                    if (window.appCore && window.appCore.state.departments.length) {
                        const dept = window.appCore.state.departments.find(d => d._id === timetable.department_id);
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
                showToast('Error loading timetables', 'error');
            });
    };

    /**
     * Format date from MongoDB ObjectId
     * @param {string} objectId - MongoDB ObjectId
     * @returns {string} - Formatted date string
     */
    const formatDate = (objectId) => {
        // Extract timestamp from MongoDB ObjectId
        const timestamp = parseInt(objectId.substring(0, 8), 16) * 1000;
        const date = new Date(timestamp);
        
        // Format date: MM/DD/YYYY
        return `${date.getMonth() + 1}/${date.getDate()}/${date.getFullYear()}`;
    };

    return {
        init() {
            initNavigation();
            initYearTabs();
            initViewSection();
            initImportSection();
        },
        showSection,
        showToast,
        showLoadingState,
        hideLoadingState,
        updateDepartmentDropdowns,
        importTimetable,
        formatDate
    };
})();

// Export the UI module
window.ui = ui;
