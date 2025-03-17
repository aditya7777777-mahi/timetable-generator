# Timetable Generator Project Instructions

## Project Overview
This is a web-based Timetable Generator application designed for educational institutions to automate the creation of academic schedules. The core functionality uses a backtracking algorithm to generate conflict-free timetables based on input constraints including departments, teachers, subjects, rooms, and time slots.

## Technology Stack
- **Frontend**: HTML5, Tailwind CSS, JavaScript (modular pattern)
- **Backend**: Python 3.7+ with Flask framework
- **Database**: MongoDB 
- **API**: RESTful architecture with JSON payloads

## Project Structure
- `client/`: Frontend code
  - `index.html`: Main application entry point
  - `index.css`: Custom styles beyond Tailwind
  - `js/`: JavaScript modules
    - `api.js`: API communication functions
    - `ui.js`: DOM manipulation utilities
    - `forms.js`: Form handling and validation
    - `app.js`: Core application logic
    - `timetableRenderer.js`: Timetable visualization
    - `core.js`: State management
    - `main.js`: Entry point and initialization
- `server/`: Backend code
  - `app.py`: Flask application and API routes
  - `timetable_generator.py`: Algorithm implementation
  - `models/`: Data models
  - `utils/`: Helper functions

## Key Functionality
1. **Entity Management**:
   - Departments (add, edit, delete, list)
   - Teachers with subject specializations
   - Subjects (lectures and practical sessions)
   - Rooms (classrooms and laboratories)
   - Time slots configuration

2. **Timetable Generation**:
   - Constraint-based backtracking algorithm
   - Conflict resolution (teacher, room, class availability)
   - Optimization for teacher preferences and resource utilization

3. **User Interface**:
   - Dashboard with summary statistics
   - Dynamic timetable views (by teacher, class, room)
   - Export functionality (PDF, Excel)
   - Import existing data

## Coding Patterns

### Frontend
- Use modular JavaScript with revealing module pattern
- Maintain clean separation of concerns (API calls, UI updates, event handling)
- Follow camelCase for variables and functions
- Prefix functions with module name when appropriate (e.g., `ui.renderTable()`, `api.getDepartments()`)
- Use async/await for API calls with proper error handling

```javascript
// Example pattern for API calls
async function fetchData() {
  try {
    const data = await api.getData();
    ui.updateView(data);
  } catch (error) {
    ui.showError(error.message);
  }
}
```

### Backend
- Follow RESTful API design principles
- Use snake_case for Python variables and functions
- Implement proper error handling with appropriate HTTP status codes
- Document API endpoints with input/output specifications
- Modularize algorithm components for better testability

```python
# Example pattern for API endpoint
@app.route('/api/departments', methods=['GET'])
def get_departments():
    try:
        departments = db.get_all_departments()
        return jsonify(departments), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

## Algorithm Constraints
- Teachers cannot be scheduled for multiple classes at the same time
- Rooms cannot host multiple sessions simultaneously
- Each subject requires a specific number of lectures and practical sessions per week
- Practical sessions may need to be scheduled for all branches simultaneously
- Room assignments must match session type (classroom for lectures, lab for practicals)
- Consider teacher preferences and availability windows
- Minimize gaps in student schedules

## Naming Conventions
- JavaScript: camelCase for variables and functions
- Python: snake_case for variables and functions
- HTML: kebab-case for element IDs and classes
- Database collections: PascalCase (Departments, Teachers, etc.)

## Common Terminology
- Department: Academic department or branch of study
- Section: Subdivision of a class for smaller group teaching
- Lecture: Theory session for a subject
- Practical: Laboratory session for a subject
- Slot: Specific time period in the timetable (e.g., Monday 9-10 AM)
- SE/TE/BE: Second Year/Third Year/Bachelor of Engineering (academic years)

When suggesting improvements or generating code, please maintain this structure and follow the established patterns. Focus on modular design, clean separation of concerns, and robust error handling.



