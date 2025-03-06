# Timetable Generator

A web application for generating college timetables using a backtracking algorithm. This application allows users to input departments, teachers, subjects, and rooms, and then automatically generates optimized timetables that avoid scheduling conflicts.

## Features

- **Department Management**: Add and view departments with multiple branches
- **Teacher Management**: Add and view teachers with their specializations
- **Subject Management**: Add and view subjects (lectures and practicals) linked to departments
- **Room Management**: Add and view rooms (classrooms and labs) with their capacity
- **Timetable Generation**: Generate conflict-free timetables using a backtracking algorithm
- **Timetable Viewing**: View and filter generated timetables by department

## Technology Stack

- **Backend**:
  - Python with Flask for the web server
  - MongoDB for database storage
  - Backtracking algorithm for timetable generation

- **Frontend**:
  - HTML5 for structure
  - Tailwind CSS for styling
  - JavaScript for client-side functionality

## Project Structure

```
timetable-generator/
├── client/                    # Frontend files
│   ├── index.html             # Main HTML file
│   ├── index.js               # JavaScript for frontend functionality
│   └── index.css              # Custom CSS styles
├── server/                    # Backend files
│   ├── app.py                 # Main Flask application 
│   └── timetable_generator.py # Backtracking algorithm implementation
├── .env                       # Environment variables
├── README.md                  # Project documentation
└── requirements.txt           # Python dependencies
```

## Installation and Setup

### Prerequisites

- Python 3.7+
- MongoDB
- Node.js and npm (optional, for development)

### Setup Instructions

1. Clone the repository:
   ```
   git clone <repository-url>
   cd timetable-generator
   ```

2. Create a virtual environment and install dependencies:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Make sure MongoDB is running on your machine:
   ```
   # Start MongoDB if not running as a service
   mongod
   ```

4. Set up environment variables:
   - Review the `.env` file and modify if needed

5. Run the application:
   ```
   flask run
   ```

6. Access the application in your browser:
   ```
   http://localhost:5000
   ```

## How to Use

1. **Add Departments**:
   - Navigate to the Departments tab
   - Fill out the department form with name, academic year, and number of branches
   - Submit the form to add the department

2. **Add Teachers**:
   - Navigate to the Teachers tab
   - Enter teacher details including code, name, and specialization
   - Submit the form to add the teacher

3. **Add Subjects**:
   - Navigate to the Subjects tab
   - Enter subject details including code, name, associated department, and type
   - Submit the form to add the subject

4. **Add Rooms**:
   - Navigate to the Rooms tab
   - Enter room details including number, capacity, and type
   - Submit the form to add the room

5. **Generate Timetable**:
   - Navigate to the Generate Timetable tab
   - Select a department and academic year
   - Click the Generate Timetable button

6. **View Timetables**:
   - Navigate to the View Timetables tab
   - Optionally filter by department
   - Click on a timetable to view its details

## Timetable Generation Algorithm

The application uses a backtracking algorithm to generate timetables. The algorithm considers various constraints:

1. Teachers cannot be scheduled for multiple classes at the same time
2. Rooms cannot be used for multiple classes at the same time
3. Each subject has a maximum number of lectures per week
4. Practical sessions may require all branches to have them simultaneously
5. Rooms must match the class type (classroom for lectures, lab for practicals)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- Terna Engineering College
- Department of Artificial Intelligence and Data Science
