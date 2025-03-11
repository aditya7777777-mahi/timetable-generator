/**
 * Core Application Module
 * Central module to manage application state and core functions
 */

const appCore = (() => {
    // Private state
    const state = {
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
     * Load all initial data from APIs
     * @returns {Promise} Promise that resolves when all data is loaded
     */
    const loadInitialData = () => {
        window.ui.showLoadingState();
        return Promise.all([
            window.api.fetchDepartments(),
            window.api.fetchTeachers(),
            window.api.fetchSubjects(),
            window.api.fetchRooms(),
            window.api.fetchTimetables()
        ]).then(([departments, teachers, subjects, rooms, timetables]) => {
            // Store data in state
            state.departments = departments;
            state.teachers = teachers;
            state.subjects = subjects;
            state.rooms = rooms;
            state.timetables = timetables;
            
            // Update UI with initial data
            window.ui.updateDepartmentDropdowns(departments);
        }).finally(() => {
            window.ui.hideLoadingState();
        });
    };

    // Public API
    return {
        // Expose state for use by other modules
        state,

        /**
         * Initialize the application
         */
        init() {
            // Initialize API module
            if (window.api) {
                window.api.init();
            }
            
            // Initialize UI module
            if (window.ui) {
                window.ui.init();
            }
            
            // Initialize forms module
            if (window.forms) {
                window.forms.init();
            }
            
            // Load initial data
            loadInitialData();
            
            // Default to departments section
            window.ui.showSection('departments');
        },

        /**
         * Update the current timetable data
         * @param {Object} timetableData - The new timetable data
         */
        updateTimetable(timetableData) {
            if (!timetableData) return;
            
            this.state.currentTimetable = timetableData;
            
            // Group timetables by year
            const yearTables = {
                SE: {},
                TE: {},
                BE: {}
            };
            
            // Sort timetable data by year
            if (timetableData.timetable) {
                Object.entries(timetableData.timetable).forEach(([key, value]) => {
                    const year = key.split('_')[0]; // SE, TE, BE
                    if (yearTables[year]) {
                        yearTables[year][key] = value;
                    }
                });
            }
            
            this.state.yearTables = yearTables;
        },
        
        /**
         * Get available years from the current timetable
         * @returns {string[]} - Array of available years (SE, TE, BE)
         */
        getAvailableYears() {
            return Object.keys(this.state.yearTables)
                .filter(year => Object.keys(this.state.yearTables[year]).length > 0);
        },
        
        /**
         * Refresh departments data
         * @returns {Promise} Promise that resolves when departments are refreshed
         */
        refreshDepartments() {
            return window.api.fetchDepartments()
                .then(departments => {
                    this.state.departments = departments;
                    window.ui.updateDepartmentDropdowns(departments);
                    return departments;
                });
        },
        
        /**
         * Refresh teachers data
         * @returns {Promise} Promise that resolves when teachers are refreshed
         */
        refreshTeachers() {
            return window.api.fetchTeachers()
                .then(teachers => {
                    this.state.teachers = teachers;
                    return teachers;
                });
        },
        
        /**
         * Refresh subjects data
         * @returns {Promise} Promise that resolves when subjects are refreshed
         */
        refreshSubjects() {
            return window.api.fetchSubjects()
                .then(subjects => {
                    this.state.subjects = subjects;
                    return subjects;
                });
        },
        
        /**
         * Refresh rooms data
         * @returns {Promise} Promise that resolves when rooms are refreshed
         */
        refreshRooms() {
            return window.api.fetchRooms()
                .then(rooms => {
                    this.state.rooms = rooms;
                    return rooms;
                });
        },
        
        /**
         * Refresh timetables data
         * @returns {Promise} Promise that resolves when timetables are refreshed
         */
        refreshTimetables() {
            return window.api.fetchTimetables()
                .then(timetables => {
                    this.state.timetables = timetables;
                    return timetables;
                });
        }
    };
})();

// Export the app core module
window.appCore = appCore;

// Initialize the app when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    appCore.init();
});
