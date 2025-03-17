/**
 * API module for handling all server communication
 */
const api = (() => {
    const handleApiError = async (response) => {
        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.message || 'API request failed');
        }
        return response.json();
    };

    return {
        init() {
            // No initialization needed currently
        },

        // Department APIs
        async fetchDepartments() {
            const response = await fetch('/api/departments');
            return handleApiError(response);
        },

        async createDepartment(departmentData) {
            const response = await fetch('/api/departments', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(departmentData)
            });
            return handleApiError(response);
        },

        async deleteDepartment(departmentId) {
            const response = await fetch(`/api/departments/${departmentId}`, {
                method: 'DELETE'
            });
            return handleApiError(response);
        },

        // Teacher APIs
        async fetchTeachers() {
            const response = await fetch('/api/teachers');
            return handleApiError(response);
        },

        async createTeacher(teacherData) {
            const response = await fetch('/api/teachers', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(teacherData)
            });
            return handleApiError(response);
        },

        async deleteTeacher(teacherId) {
            const response = await fetch(`/api/teachers/${teacherId}`, {
                method: 'DELETE'
            });
            return handleApiError(response);
        },

        // Subject APIs
        async fetchSubjects() {
            const response = await fetch('/api/subjects');
            return handleApiError(response);
        },

        async createSubject(subjectData) {
            const response = await fetch('/api/subjects', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(subjectData)
            });
            return handleApiError(response);
        },

        async deleteSubject(subjectId) {
            const response = await fetch(`/api/subjects/${subjectId}`, {
                method: 'DELETE'
            });
            return handleApiError(response);
        },

        // Room APIs
        async fetchRooms() {
            const response = await fetch('/api/rooms');
            return handleApiError(response);
        },

        async createRoom(roomData) {
            const response = await fetch('/api/rooms', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(roomData)
            });
            return handleApiError(response);
        },

        async deleteRoom(roomId) {
            const response = await fetch(`/api/rooms/${roomId}`, {
                method: 'DELETE'
            });
            return handleApiError(response);
        },

        // Timetable APIs
        async fetchTimetables() {
            const response = await fetch('/api/timetables');
            return handleApiError(response);
        },

        async fetchTimetableById(timetableId) {
            const response = await fetch(`/api/timetables/${timetableId}`);
            return handleApiError(response);
        },

        async getFormattedTimetable(timetableId) {
            const response = await fetch(`/api/timetables/${timetableId}/formatted`);
            return handleApiError(response);
        },

        async generateTimetable(timetableData) {
            const response = await fetch('/api/generate-timetable', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(timetableData)
            });
            return handleApiError(response);
        },

        async importTimetable(timetableData) {
            const response = await fetch('/api/timetables/import', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(timetableData)
            });
            return handleApiError(response);
        },

        async deleteTimetable(timetableId) {
            const response = await fetch(`/api/timetables/${timetableId}`, {
                method: 'DELETE'
            });
            return handleApiError(response);
        }
    };
})();

// Export the API module
window.api = api;