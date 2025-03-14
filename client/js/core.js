/**
 * Core application functionality 
 * Handles app initialization and global state management
 */

// Global state management
const appState = {
    departments: [],
    teachers: [],
    subjects: [],
    rooms: [],
    timetables: [],
    currentTimetable: null,
    yearTables: {
        SE: {},
        TE: {},
        BE: {}
    }
};

/**
 * Initialize the application
 */
function initApp() {
    // Add event listeners for navigation
    initNavigation();
    
    // Load initial data
    loadInitialData();
    
    // Initialize year tab event listeners
    initYearTabs();
    
    // Initialize form submissions
    initFormHandlers();
    
    // Show the default section
    showSection('departments');
}

/**
 * Initialize navigation event listeners
 */
function initNavigation() {
    const navButtons = document.querySelectorAll('.nav-btn');
    
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
            document.querySelectorAll('.section').forEach(section => {
                section.classList.add('hidden');
            });
            document.getElementById(sectionId).classList.remove('hidden');
        });
    });
    
    // Add specific event listeners for each nav button
    document.getElementById('nav-departments').addEventListener('click', () => showSection('departments'));
    document.getElementById('nav-teachers').addEventListener('click', () => showSection('teachers'));
    document.getElementById('nav-subjects').addEventListener('click', () => showSection('subjects'));
    document.getElementById('nav-rooms').addEventListener('click', () => showSection('rooms'));
    document.getElementById('nav-generate').addEventListener('click', () => showSection('generate'));
    document.getElementById('nav-view').addEventListener('click', () => showSection('view'));
    document.getElementById('nav-import').addEventListener('click', () => showSection('import'));
}

/**
 * Show a specific section and hide others
 * @param {string} sectionId - ID of the section to show (without '-section' suffix)
 */
function showSection(sectionId) {
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
}

/**
 * Initialize year tab event listeners
 */
function initYearTabs() {
    document.getElementById('se-year-tab').addEventListener('click', function() { 
        activateYearTab('SE'); 
    });
    
    document.getElementById('te-year-tab').addEventListener('click', function() { 
        activateYearTab('TE'); 
    });
    
    document.getElementById('be-year-tab').addEventListener('click', function() { 
        activateYearTab('BE'); 
    });
}

/**
 * Load initial data from API endpoints
 */
function loadInitialData() {
    showLoadingState();
    Promise.all([
        api.fetchDepartments(),
        api.fetchTeachers(),
        api.fetchSubjects(),
        api.fetchRooms(),
        api.fetchTimetables()
    ]).then(([departments, teachers, subjects, rooms, timetables]) => {
        // Store data in global state
        appState.departments = departments;
        appState.teachers = teachers;
        appState.subjects = subjects;
        appState.rooms = rooms;
        appState.timetables = timetables;
    }).finally(() => {
        hideLoadingState();
    });
}

/**
 * Initialize all form submission handlers
 */
function initFormHandlers() {
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
    
    // Add import timetable handler
    document.getElementById('import-timetable-btn').addEventListener('click', importTimetable);
}

// Export functions and state to be used by other modules
window.appCore = {
    initApp,
    showSection,
    state: appState
};