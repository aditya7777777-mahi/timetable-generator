/**
 * Main application entry point
 * Responsible for initializing the entire application
 */

// Wait for DOM to be fully loaded before initializing the application
document.addEventListener('DOMContentLoaded', () => {
    console.log('Initializing timetable generator application...');
    
    // Initialize all modules in the correct order
    if (window.api) {
        window.api.init();
    }
    
    if (window.ui) {
        window.ui.init();
    }
    
    if (window.forms) {
        window.forms.init();
    }
    
    if (window.appCore) {
        window.appCore.init();
    }
});
