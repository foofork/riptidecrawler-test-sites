// Analytics Script (Simulated)

(function() {
    'use strict';

    console.log('Analytics.js loaded');

    // Simulate analytics tracking
    const analytics = {
        pageView: function(page) {
            console.log('Analytics: Page view tracked -', page);
            return { event: 'pageview', page: page, timestamp: Date.now() };
        },

        trackEvent: function(category, action, label) {
            console.log('Analytics: Event tracked -', { category, action, label });
            return { event: 'track', category, action, label, timestamp: Date.now() };
        },

        trackTiming: function(category, variable, time) {
            console.log('Analytics: Timing tracked -', { category, variable, time });
            return { event: 'timing', category, variable, time, timestamp: Date.now() };
        }
    };

    // Track initial page load
    window.addEventListener('load', function() {
        const loadTime = performance.timing.loadEventEnd - performance.timing.navigationStart;
        analytics.pageView(window.location.pathname);
        analytics.trackTiming('Page Load', 'Total Time', loadTime);
        console.log('Page load time:', loadTime + 'ms');
    });

    // Track resource timings
    window.addEventListener('load', function() {
        const resources = performance.getEntriesByType('resource');
        resources.forEach(resource => {
            if (resource.initiatorType === 'css' || resource.initiatorType === 'script' || resource.initiatorType === 'img') {
                console.log('Resource timing:', {
                    name: resource.name,
                    type: resource.initiatorType,
                    duration: resource.duration.toFixed(2) + 'ms'
                });
            }
        });
    });

    // Make analytics globally available
    window.analytics = analytics;

    console.log('Analytics initialized');
})();
