/**
 * Timetable Renderer Module
 * Handles all functionality related to rendering timetables
 */

const timetableRenderer = (() => {
    // Private utility functions
    /**
     * Compare two time slots for chronological sorting
     * @param {string} a - First time slot (e.g. "9:00 am")
     * @param {string} b - Second time slot (e.g. "10:00 am")
     * @returns {number} - Comparison result for sorting
     */
    const compareTimeSlots = (a, b) => {
        // Extract hour from time slot for proper chronological sorting
        const getTimeValue = (timeStr) => {
            const match = timeStr.match(/(\d+):(\d+)\s*(am|pm)/i);
            if (match) {
                let hours = parseInt(match[1]);
                const minutes = parseInt(match[2]);
                const ampm = match[3].toLowerCase();
                
                // Convert to 24-hour format for comparison
                if (ampm === 'pm' && hours < 12) hours += 12;
                if (ampm === 'am' && hours === 12) hours = 0;
                
                return hours * 60 + minutes;
            }
            return 0;
        };
        
        return getTimeValue(a) - getTimeValue(b);
    };

    /**
     * Get CSS class for a cell based on its type
     * @param {object} cellData - Cell data with type information
     * @returns {string} - CSS class string
     */
    const getCellClass = (cellData) => {
        let cellClass = 'border p-2 timetable-cell';
        
        if (cellData?.type === 'break') {
            cellClass += ' break-cell';
        } else if (cellData?.type === 'practical') {
            cellClass += ' practical-cell';
        } else if (cellData?.type === 'lecture') {
            cellClass += ' lecture-cell';
        }
        
        return cellClass;
    };

    // Public API
    return {
        /**
         * Display a timetable for a specific year
         * @param {string} year - The year to display (SE, TE, BE)
         * @param {Object} yearData - Timetable data for the year
         */
        showYearTimetable(year, yearData) {
            const yearsContentContainer = document.getElementById('years-content');
            if (!yearsContentContainer) return;
            
            yearsContentContainer.innerHTML = ''; // Clear previous content
            
            if (!yearData || Object.keys(yearData).length === 0) {
                yearsContentContainer.innerHTML = `<div class="text-gray-500 italic">No timetable data available for ${year} year</div>`;
                return;
            }
            
            // Create main timetable first
            if (yearData[`${year}_Main`]) {
                const mainSection = document.createElement('div');
                mainSection.className = 'mb-8';
                mainSection.innerHTML = `<h4 class="text-lg font-semibold mb-2">Main Class Timetable</h4>`;
                this.createTimetableView(mainSection, yearData[`${year}_Main`]);
                yearsContentContainer.appendChild(mainSection);
            }
            
            // Create batch timetables
            ['B1', 'B2', 'B3'].forEach(batch => {
                const batchKey = `${year}_${batch}`;
                if (yearData[batchKey]) {
                    const batchSection = document.createElement('div');
                    batchSection.className = 'mb-8';
                    batchSection.innerHTML = `<h4 class="text-lg font-semibold mb-2">Batch ${batch} Timetable</h4>`;
                    this.createTimetableView(batchSection, yearData[batchKey]);
                    yearsContentContainer.appendChild(batchSection);
                }
            });
        },

        /**
         * Create a timetable view and append it to the container
         * @param {HTMLElement} container - Container to append the timetable to
         * @param {Object} timetableData - Timetable data to render
         */
        createTimetableView(container, timetableData) {
            const table = document.createElement('table');
            table.className = 'min-w-full border-collapse border';
            
            // Create header row
            const thead = document.createElement('thead');
            const headerRow = document.createElement('tr');
            
            // Add DAY/TIME cell
            headerRow.innerHTML = '<th class="border p-2 bg-gray-100">DAY/TIME</th>';
            
            // Get all time slots and sort them chronologically
            const timeSlots = Object.keys(timetableData['MONDAY']).sort(compareTimeSlots);
            
            // Add time slots to header
            timeSlots.forEach(slot => {
                headerRow.innerHTML += `<th class="border p-2 bg-gray-100 text-sm">${slot}</th>`;
            });
            
            thead.appendChild(headerRow);
            table.appendChild(thead);
            
            // Create table body with days in chronological order
            const tbody = document.createElement('tbody');
            
            // Define days in chronological order
            const orderedDays = ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY'];
            
            orderedDays.forEach(day => {
                const row = document.createElement('tr');
                row.innerHTML = `<td class="border p-2 font-semibold">${day}</td>`;
                
                timeSlots.forEach(slot => {
                    const cellData = timetableData[day][slot];
                    let cellContent = '';
                    let cellClass = getCellClass(cellData);
                    
                    if (cellData.type === 'break') {
                        cellContent = 'BREAK';
                    } else if (cellData.subject) {
                        cellContent = cellData.subject;
                        if (cellData.teacher) cellContent += ` - ${cellData.teacher}`;
                        if (cellData.room) cellContent += `\n${cellData.room}`;
                        if (cellData.batch) cellContent += `\n${cellData.batch}`;
                    }
                    
                    row.innerHTML += `<td class="${cellClass}">${cellContent}</td>`;
                });
                
                tbody.appendChild(row);
            });
            
            table.appendChild(tbody);
            container.appendChild(table);
        },

        /**
         * Display a formatted timetable
         * @param {Object} timetable - Timetable data
         * @param {Object} department - Department data
         */
        displayFormattedTimetable(timetable, department) {
            // Set headers
            document.getElementById('college-name').textContent = 'TERNA ENGINEERING COLLEGE';
            document.getElementById('department-name').textContent = department ? 
                `DEPARTMENT OF ${department.name.toUpperCase()}` : 
                'DEPARTMENT OF ARTIFICIAL INTELLIGENCE AND DATA SCIENCE';
            
            // Set class info and academic year
            const classPrefix = Object.keys(timetable.timetable)[0].split('_')[0]; // First part of class key (e.g., "TE" from "TE_Main")
            document.getElementById('class-info').textContent = `CLASS: ${classPrefix}-A`;
            document.getElementById('academic-year').textContent = `AY: ${timetable.academic_year}`;
            
            // Show header
            document.getElementById('timetable-header').classList.remove('hidden');
            
            // Generate timetable
            const timetableContainer = document.getElementById('timetable-view');
            timetableContainer.innerHTML = '';
            
            // Container for year content
            const yearsContentContainer = document.createElement('div');
            yearsContentContainer.id = 'years-content';
            timetableContainer.appendChild(yearsContentContainer);
            
            // Group timetables by year
            const yearTables = {
                SE: {},
                TE: {},
                BE: {}
            };
            
            // Sort timetable data by year
            if (timetable.timetable) {
                Object.entries(timetable.timetable).forEach(([key, value]) => {
                    const year = key.split('_')[0]; // SE, TE, BE
                    if (yearTables[year]) {
                        yearTables[year][key] = value;
                    }
                });
            }
            
            // Store the current timetable data for access by tab handlers
            if (window.appCore && window.appCore.state) {
                window.appCore.state.yearTables = yearTables;
            }

            // Show the year tabs container
            const yearTabsContainer = document.getElementById('year-tabs-container');
            yearTabsContainer.classList.remove('hidden');
            
            // Check which tabs should be enabled based on available data
            const availableYears = Object.keys(yearTables).filter(year => Object.keys(yearTables[year]).length > 0);
            
            // Show the first available year by default, or "SE" if none
            const defaultYear = availableYears.length > 0 ? availableYears[0] : 'SE';
            
            // Try to use UI module if available, otherwise fall back to direct DOM manipulation
            if (window.ui && typeof window.ui.activateYearTab === 'function') {
                window.ui.activateYearTab(defaultYear);
            } else {
                // Fallback to direct tab activation
                this.activateYearTab(defaultYear);
            }
            
            // Populate faculty and subject details
            this.populateFacultySubjectDetails(timetable);
            document.getElementById('faculty-subject-details').classList.remove('hidden');
        },

        /**
         * Activate a year tab
         * @param {string} year - Year to activate (SE, TE, BE)
         */
        activateYearTab(year) {
            // Update active tab styling
            document.querySelectorAll('.year-tab').forEach(tab => {
                tab.classList.remove('active');
            });
            document.getElementById(`${year.toLowerCase()}-year-tab`).classList.add('active');
            
            // Update class info
            document.getElementById('class-info').textContent = `CLASS: ${year}-A`;
            
            // Get year table data from state
            let yearData = {};
            if (window.appCore && window.appCore.state && window.appCore.state.yearTables) {
                yearData = window.appCore.state.yearTables[year];
            }
            
            // Show corresponding year's timetable
            this.showYearTimetable(year, yearData);
        },
        
        /**
         * Populate faculty and subject details in the tables
         * @param {Object} timetable - Timetable data
         */
        populateFacultySubjectDetails(timetable) {
            const facultyTable = document.getElementById('faculty-table').querySelector('tbody');
            const subjectTable = document.getElementById('subject-table').querySelector('tbody');
            
            facultyTable.innerHTML = '';
            subjectTable.innerHTML = '';
            
            // Extract unique teachers and subjects
            const teachers = new Map();
            const subjects = new Map();
            
            // Loop through all timetable data
            Object.values(timetable.timetable).forEach(yearData => {
                Object.values(yearData).forEach(dayData => {
                    Object.values(dayData).forEach(slot => {
                        if (slot.teacher && slot.subject && slot.type !== 'break') {
                            teachers.set(slot.teacher, true);
                            subjects.set(slot.subject, true);
                        }
                    });
                });
            });
            
            // Add teachers to table
            Array.from(teachers.keys()).sort().forEach(teacher => {
                const row = document.createElement('tr');
                
                const codeCell = document.createElement('td');
                codeCell.className = 'border p-2';
                codeCell.textContent = teacher;
                
                const nameCell = document.createElement('td');
                nameCell.className = 'border p-2';
                // We don't have full names in the data, so just showing code
                nameCell.textContent = teacher;
                
                row.appendChild(codeCell);
                row.appendChild(nameCell);
                facultyTable.appendChild(row);
            });
            
            // Add subjects to table
            Array.from(subjects.keys()).sort().forEach(subject => {
                const row = document.createElement('tr');
                
                const codeCell = document.createElement('td');
                codeCell.className = 'border p-2';
                codeCell.textContent = subject;
                
                const nameCell = document.createElement('td');
                nameCell.className = 'border p-2';
                // We don't have full names in the data, so just showing code
                nameCell.textContent = subject;
                
                row.appendChild(codeCell);
                row.appendChild(nameCell);
                subjectTable.appendChild(row);
            });
        },

        /**
         * Generate HTML for a timetable
         * @param {string} key - Key identifier for the timetable
         * @param {Object} data - Timetable data
         * @param {string} title - Title for the timetable section
         * @returns {string} - HTML string for the timetable
         */
        generateTimetableHTML(key, data, title) {
            let html = `
                <div class="timetable-section mb-6">
                    <h4 class="text-lg font-semibold mb-2">${title}</h4>
                    <div class="overflow-x-auto">
                        <table class="min-w-full border border-gray-300">
                            <thead>
                                <tr>
                                    <th class="border border-gray-300 bg-gray-100 px-4 py-2">Time/Day</th>
            `;

            // Use days in chronological order
            const orderedDays = ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY'];
            const availableDays = orderedDays.filter(day => data[day]);
            
            // Add days to header
            availableDays.forEach(day => {
                html += `<th class="border border-gray-300 bg-gray-100 px-4 py-2">${day}</th>`;
            });

            html += `</tr></thead><tbody>`;

            // Get time slots from the first day
            if (availableDays.length > 0) {
                // Sort time slots chronologically
                const timeSlots = Object.keys(data[availableDays[0]]).sort(compareTimeSlots);

                timeSlots.forEach(timeSlot => {
                    html += `<tr>
                        <td class="border border-gray-300 px-4 py-2 font-semibold">${timeSlot}</td>`;

                    availableDays.forEach(day => {
                        const cellData = data[day][timeSlot];
                        const isBreak = cellData?.type === 'break';
                        const isPractical = cellData?.type === 'practical';
                        const isLecture = cellData?.type === 'lecture';

                        let cellClass = 'border border-gray-300 px-4 py-2 ';
                        if (isBreak) cellClass += 'bg-gray-100';
                        else if (isPractical) cellClass += 'bg-blue-50';
                        else if (isLecture) cellClass += 'bg-green-50';

                        html += `<td class="${cellClass}">`;
                        if (cellData?.subject) {
                            if (isBreak) {
                                html += `<div class="text-center font-medium">BREAK</div>`;
                            } else {
                                html += `
                                    <div class="font-semibold">${cellData.subject}</div>
                                    ${cellData.teacher ? `<div class="text-sm text-gray-600">${cellData.teacher}</div>` : ''}
                                    ${cellData.room ? `<div class="text-sm text-gray-600">Room: ${cellData.room}</div>` : ''}
                                    ${cellData.batch ? `<div class="text-xs text-blue-600">Batch: ${cellData.batch}</div>` : ''}
                                    <div class="text-xs text-gray-500">${cellData.type || 'lecture'}</div>
                                `;
                            }
                        } else {
                            html += '-';
                        }
                        html += '</td>';
                    });

                    html += '</tr>';
                });
            }

            html += `</tbody></table></div></div>`;
            return html;
        },

        /**
         * Render a timetable into a specific display element
         * @param {Object} timetableData - Timetable data to render
         * @param {string} type - Type of timetable to render (class, teacher, room)
         */
        renderTimetable(timetableData, type = 'class') {
            const timetableDisplay = document.getElementById(`timetable-display-${type}`);
            if (!timetableDisplay) {
                console.error(`Timetable display element not found for type: ${type}`);
                return;
            }
            
            // Check if there is timetable data
            if (!timetableData || Object.keys(timetableData).length === 0) {
                timetableDisplay.innerHTML = '<div class="text-gray-500 italic">No timetable data available</div>';
                return;
            }

            // Group timetables by year
            const yearGroups = {
                SE: {},
                TE: {},
                BE: {}
            };

            // Sort and group timetables by year
            Object.keys(timetableData).forEach(key => {
                const year = key.split('_')[0]; // SE, TE, BE
                const type = key.split('_')[1]; // Main, B1, B2, B3
                if (yearGroups[year]) {
                    yearGroups[year][key] = timetableData[key];
                }
            });

            let finalHtml = '';

            // Create timetables for each year
            Object.keys(yearGroups).forEach(year => {
                const yearData = yearGroups[year];
                if (Object.keys(yearData).length === 0) return;

                // Create section for this year
                finalHtml += `<div class="year-section mb-8">
                    <h3 class="text-xl font-bold mb-4">${year} Year Timetables</h3>`;

                // First display the main timetable
                const mainKey = `${year}_Main`;
                if (yearData[mainKey]) {
                    finalHtml += this.generateTimetableHTML(mainKey, yearData[mainKey], 'Main Lectures');
                }

                // Then display batch timetables if they exist
                ['B1', 'B2', 'B3'].forEach(batch => {
                    const batchKey = `${year}_${batch}`;
                    if (yearData[batchKey]) {
                        finalHtml += this.generateTimetableHTML(batchKey, yearData[batchKey], `Batch ${batch} Practicals`);
                    }
                });

                finalHtml += '</div>';
            });

            timetableDisplay.innerHTML = finalHtml;
        }
    };
})();

// Export the timetable renderer module
window.timetableRenderer = timetableRenderer;