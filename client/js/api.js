/**
 * API module for handling all server communication
 */

const api = (() => {
    return {
        /**
         * Initialize the API module
         */
        init() {
            // No initialization needed for now
        },

        /**
         * Fetch departments from server
         * @returns {Promise<Array>} Array of department objects
         */
        async fetchDepartments() {
            const response = await fetch('/api/departments');
            if (!response.ok) {
                throw new Error('Failed to fetch departments');
            }
            return response.json();
        },

        /**
         * Create a new department
         * @param {Object} departmentData - The department data to create
         * @returns {Promise<Object>} Created department object
         */
        async createDepartment(departmentData) {
            const response = await fetch('/api/departments', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(departmentData)
            });
            if (!response.ok) {
                throw new Error('Failed to create department');
            }
            return response.json();
        },

        /**
         * Delete a department
         * @param {string} departmentId - ID of department to delete
         */
        async deleteDepartment(departmentId) {
            const response = await fetch(`/api/departments/${departmentId}`, {
                method: 'DELETE'
            });
            if (!response.ok) {
                throw new Error('Failed to delete department');
            }
        },

        /**
         * Fetch teachers from server
         * @returns {Promise<Array>} Array of teacher objects
         */
        async fetchTeachers() {
            const response = await fetch('/api/teachers');
            if (!response.ok) {
                throw new Error('Failed to fetch teachers');
            }
            return response.json();
        },

        /**
         * Create a new teacher
         * @param {Object} teacherData - The teacher data to create
         * @returns {Promise<Object>} Created teacher object
         */
        async createTeacher(teacherData) {
            const response = await fetch('/api/teachers', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(teacherData)
            });
            if (!response.ok) {
                throw new Error('Failed to create teacher');
            }
            return response.json();
        },

        /**
         * Delete a teacher
         * @param {string} teacherId - ID of teacher to delete
         */
        async deleteTeacher(teacherId) {
            const response = await fetch(`/api/teachers/${teacherId}`, {
                method: 'DELETE'
            });
            if (!response.ok) {
                throw new Error('Failed to delete teacher');
            }
        },

        /**
         * Fetch subjects from server
         * @returns {Promise<Array>} Array of subject objects
         */
        async fetchSubjects() {
            const response = await fetch('/api/subjects');
            if (!response.ok) {
                throw new Error('Failed to fetch subjects');
            }
            return response.json();
        },

        /**
         * Create a new subject
         * @param {Object} subjectData - The subject data to create
         * @returns {Promise<Object>} Created subject object
         */
        async createSubject(subjectData) {
            const response = await fetch('/api/subjects', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(subjectData)
            });
            if (!response.ok) {
                throw new Error('Failed to create subject');
            }
            return response.json();
        },

        /**
         * Delete a subject
         * @param {string} subjectId - ID of subject to delete
         */
        async deleteSubject(subjectId) {
            const response = await fetch(`/api/subjects/${subjectId}`, {
                method: 'DELETE'
            });
            if (!response.ok) {
                throw new Error('Failed to delete subject');
            }
        },

        /**
         * Fetch rooms from server
         * @returns {Promise<Array>} Array of room objects
         */
        async fetchRooms() {
            const response = await fetch('/api/rooms');
            if (!response.ok) {
                throw new Error('Failed to fetch rooms');
            }
            return response.json();
        },

        /**
         * Create a new room
         * @param {Object} roomData - The room data to create
         * @returns {Promise<Object>} Created room object
         */
        async createRoom(roomData) {
            const response = await fetch('/api/rooms', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(roomData)
            });
            if (!response.ok) {
                throw new Error('Failed to create room');
            }
            return response.json();
        },

        /**
         * Delete a room
         * @param {string} roomId - ID of room to delete
         */
        async deleteRoom(roomId) {
            const response = await fetch(`/api/rooms/${roomId}`, {
                method: 'DELETE'
            });
            if (!response.ok) {
                throw new Error('Failed to delete room');
            }
        },

        /**
         * Fetch timetables from server
         * @param {string} [departmentId] - Optional department ID to filter by
         * @returns {Promise<Array>} Array of timetable objects
         */
        async fetchTimetables(departmentId = '') {
            const url = departmentId ? `/api/timetables?department_id=${departmentId}` : '/api/timetables';
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error('Failed to fetch timetables');
            }
            return response.json();
        },

        /**
         * Get formatted timetable by ID
         * @param {string} timetableId - ID of timetable to fetch
         * @returns {Promise<Object>} Formatted timetable data
         */
        async getFormattedTimetable(timetableId) {
            const response = await fetch(`/api/timetables/${timetableId}/formatted`);
            if (!response.ok) {
                throw new Error('Failed to fetch timetable');
            }
            return response.json();
        },

        /**
         * Generate timetable
         * @param {Object} timetableData - Data needed to generate timetable
         * @returns {Promise<Object>} Generated timetable
         */
        async generateTimetable(timetableData) {
            const response = await fetch('/api/generate-timetable', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(timetableData)
            });
            if (!response.ok) {
                throw new Error('Failed to generate timetable');
            }
            return response.json();
        },

        /**
         * Import a timetable
         * @param {Object} importData - Timetable data to import
         * @returns {Promise<Object>} Imported timetable
         */
        async importTimetable(importData) {
            const response = await fetch('/api/timetables/import', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(importData)
            });
            if (!response.ok) {
                throw new Error('Failed to import timetable');
            }
            return response.json();
        }
    };
})();

// Export the API module
window.api = api;