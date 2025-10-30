/**
 * Base JavaScript for test sites
 * Minimal interactivity for demonstration
 */

// Document ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('Test site loaded');

    // Add active class to current nav item
    highlightCurrentPage();

    // Setup API data fetching
    setupDataFetching();

    // Add copy functionality for code blocks
    setupCodeCopy();
});

/**
 * Highlight current page in navigation
 */
function highlightCurrentPage() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-menu a');

    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.style.color = 'var(--primary-color)';
            link.style.fontWeight = '600';
        }
    });
}

/**
 * Setup data fetching functionality
 */
function setupDataFetching() {
    // Example: Add click handlers for data loading
    const dataLinks = document.querySelectorAll('[data-load]');

    dataLinks.forEach(link => {
        link.addEventListener('click', async (e) => {
            e.preventDefault();
            const endpoint = link.getAttribute('data-load');
            await loadData(endpoint);
        });
    });
}

/**
 * Load data from API endpoint
 */
async function loadData(endpoint) {
    try {
        const response = await fetch(endpoint);
        const data = await response.json();
        console.log('Data loaded:', data);
        // Handle data display here
        return data;
    } catch (error) {
        console.error('Error loading data:', error);
    }
}

/**
 * Setup copy functionality for code blocks
 */
function setupCodeCopy() {
    const codeBlocks = document.querySelectorAll('code');

    codeBlocks.forEach(block => {
        block.style.cursor = 'pointer';
        block.title = 'Click to copy';

        block.addEventListener('click', () => {
            const text = block.textContent;
            navigator.clipboard.writeText(text).then(() => {
                // Visual feedback
                const originalBg = block.style.backgroundColor;
                block.style.backgroundColor = 'var(--success-color)';
                block.style.color = 'white';

                setTimeout(() => {
                    block.style.backgroundColor = originalBg;
                    block.style.color = '';
                }, 200);
            });
        });
    });
}

/**
 * Fetch and display health status
 */
async function checkHealth() {
    try {
        const response = await fetch('/api/health');
        const health = await response.json();
        console.log('Health check:', health);
        return health;
    } catch (error) {
        console.error('Health check failed:', error);
        return { status: 'error' };
    }
}

/**
 * Fetch ground-truth data
 */
async function getGroundTruth() {
    try {
        const response = await fetch('/api/ground-truth');
        const data = await response.json();
        console.log('Ground truth data:', data);
        return data;
    } catch (error) {
        console.error('Error fetching ground truth:', error);
    }
}

/**
 * Format JSON for display
 */
function formatJSON(obj) {
    return JSON.stringify(obj, null, 2);
}

/**
 * Export data as JSON file
 */
function downloadJSON(data, filename = 'data.json') {
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
}

// Export functions for use in other scripts
window.testSite = {
    loadData,
    checkHealth,
    getGroundTruth,
    formatJSON,
    downloadJSON
};
