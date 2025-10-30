// Main JavaScript for Media Test Site

console.log('Main.js loaded successfully!');

// DOM Ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM is ready');

    // Add interactive behavior
    const links = document.querySelectorAll('a[href^="/static/"]');
    links.forEach(link => {
        link.addEventListener('click', function(e) {
            console.log('Resource link clicked:', this.href);
        });
    });

    // Track resource loading
    const images = document.querySelectorAll('img');
    images.forEach(img => {
        img.addEventListener('load', function() {
            console.log('Image loaded:', this.src);
        });
        img.addEventListener('error', function() {
            console.error('Image failed to load:', this.src);
        });
    });

    // Add loaded indicator
    const body = document.body;
    const indicator = document.createElement('div');
    indicator.style.cssText = 'position: fixed; bottom: 20px; right: 20px; background: #27ae60; color: white; padding: 10px 20px; border-radius: 5px; z-index: 9999; font-size: 14px;';
    indicator.textContent = '✓ All scripts loaded';
    body.appendChild(indicator);

    // Remove indicator after 3 seconds
    setTimeout(() => {
        indicator.style.opacity = '0';
        indicator.style.transition = 'opacity 1s';
        setTimeout(() => indicator.remove(), 1000);
    }, 3000);
});

// Utility function to check resource loading
function checkResourceLoading() {
    const resources = {
        css: document.styleSheets.length,
        scripts: document.scripts.length,
        images: document.images.length
    };
    console.log('Resources loaded:', resources);
    return resources;
}

// Export for testing
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { checkResourceLoading };
}
