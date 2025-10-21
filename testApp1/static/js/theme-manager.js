/**
 * IntegrityHoops Theme Manager
 * Handles theme switching between Default and Miami Heat themes
 */

(function() {
    'use strict';
    
    const THEME_KEY = 'integrityHoopsTheme';
    const THEMES = {
        DEFAULT: 'default',
        HEAT: 'heat'
    };
    
    /**
     * Get the current theme from localStorage
     */
    function getCurrentTheme() {
        return localStorage.getItem(THEME_KEY) || THEMES.DEFAULT;
    }
    
    /**
     * Set the theme in localStorage
     */
    function setTheme(theme) {
        if (theme === THEMES.DEFAULT || theme === THEMES.HEAT) {
            localStorage.setItem(THEME_KEY, theme);
            applyTheme(theme);
            return true;
        }
        return false;
    }
    
    /**
     * Apply the theme to the current page
     */
    function applyTheme(theme) {
        const head = document.head;
        
        // Remove any existing Miami Heat theme link
        const existingHeatTheme = document.getElementById('miami-heat-theme');
        if (existingHeatTheme) {
            existingHeatTheme.remove();
        }
        
        if (theme === THEMES.HEAT) {
            // Add Miami Heat theme
            const link = document.createElement('link');
            link.id = 'miami-heat-theme';
            link.rel = 'stylesheet';
            link.href = '/static/css/miami-heat-theme.css';
            head.appendChild(link);
            
            // Add theme class to body
            document.body.classList.add('theme-heat');
            document.body.classList.remove('theme-default');
            
            // Emit custom event for theme change
            window.dispatchEvent(new CustomEvent('themeChanged', { detail: { theme: THEMES.HEAT } }));
        } else {
            // Use default theme
            document.body.classList.add('theme-default');
            document.body.classList.remove('theme-heat');
            
            // Emit custom event for theme change
            window.dispatchEvent(new CustomEvent('themeChanged', { detail: { theme: THEMES.DEFAULT } }));
        }
    }
    
    /**
     * Initialize theme on page load
     */
    function initTheme() {
        const currentTheme = getCurrentTheme();
        applyTheme(currentTheme);
    }
    
    /**
     * Toggle between themes
     */
    function toggleTheme() {
        const currentTheme = getCurrentTheme();
        const newTheme = currentTheme === THEMES.HEAT ? THEMES.DEFAULT : THEMES.HEAT;
        setTheme(newTheme);
        return newTheme;
    }
    
    // Auto-initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initTheme);
    } else {
        initTheme();
    }
    
    // Expose public API
    window.IntegrityHoopsTheme = {
        getCurrentTheme: getCurrentTheme,
        setTheme: setTheme,
        toggleTheme: toggleTheme,
        THEMES: THEMES
    };
    
})();

