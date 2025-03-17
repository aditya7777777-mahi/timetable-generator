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
    // Initialize form submission handlers
    initFormHandlers();
    
    // Initialize year tab event listeners
    initYearTabs();
}

/**
 * Initialize form submission handlers
 */
function initFormHandlers() {
    document.getElementById('timetable-select')?.addEventListener('change', function() {
        const selectedId = this.value;
        if (selectedId) {
            viewTimetable(selectedId);
        }
    });
}

/**
 * Initialize year tab event listeners
 */
function initYearTabs() {
    document.querySelectorAll('.year-tab').forEach(tab => {
        tab.addEventListener('click', function() {
            const year = this.getAttribute('data-year');
            if (year) {
                window.timetableRenderer.activateYearTab(year);
            }
        });
    });
}

/**
 * View a specific timetable
 * @param {string} timetableId - ID of the timetable to view
 */
async function viewTimetable(timetableId) {
    try {
        window.ui.showLoadingState();
        const data = await window.api.getFormattedTimetable(timetableId);
        window.timetableRenderer.displayFormattedTimetable(data.timetable, data.department);
    } catch (error) {
        console.error('Error viewing timetable:', error);
        window.ui.showToast('Error viewing timetable: ' + error.message, 'error');
    } finally {
        window.ui.hideLoadingState();
    }
}

// Export functions and state to be used by other modules
window.appCore = {
    init() {
        initApp();
    },
    state: appState
};