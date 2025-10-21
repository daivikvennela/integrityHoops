/**
 * Animated Scorecard JavaScript
 * NBA 2K/Madden-style animations for basketball cognitive scorecard
 */

// Global state
let animationTimeline = [];
let isAnimating = false;

/**
 * Initialize animated scorecard with data
 */
function initializeAnimatedScorecard(data) {
    console.log('Initializing animated scorecard with data:', data);
    
    // Start animations sequence
    setTimeout(() => {
        animateCircularIndicators();
        animateHorizontalBars();
        animateShotDistribution(data);
    }, 500);
}

/**
 * Animate circular progress indicators
 */
function animateCircularIndicators() {
    const circles = document.querySelectorAll('.progress-ring-circle');
    
    circles.forEach((circle, index) => {
        const percentage = parseFloat(circle.getAttribute('data-percentage') || 0);
        const radius = circle.r.baseVal.value;
        const circumference = 2 * Math.PI * radius;
        const offset = circumference - (percentage / 100) * circumference;
        
        // Delay each circle animation
        setTimeout(() => {
            circle.style.strokeDashoffset = offset;
            animateCounter(circle.parentElement.querySelector('.circle-percentage'), 0, percentage, 2000);
        }, index * 200);
    });
}

/**
 * Animate horizontal bar charts
 */
function animateHorizontalBars() {
    const barFills = document.querySelectorAll('.bar-fill');
    const barFillsNeg = document.querySelectorAll('.bar-fill-neg');
    
    // Animate positive bars
    barFills.forEach((bar, index) => {
        const width = parseFloat(bar.getAttribute('data-width') || 0);
        setTimeout(() => {
            bar.style.width = width + '%';
        }, 1500 + (index * 100));
    });
    
    // Animate negative bars
    barFillsNeg.forEach((bar, index) => {
        const width = parseFloat(bar.getAttribute('data-width') || 0);
        setTimeout(() => {
            bar.style.width = width + '%';
        }, 1500 + (index * 100));
    });
}

/**
 * Animate shot distribution pie chart
 */
function animateShotDistribution(data) {
    const canvas = document.getElementById('shotDistributionChart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    const radius = 80;
    
    // Shot distribution data
    const shotData = data.shot_distribution || {};
    const segments = [
        { label: '3PT', value: shotData.three_pt?.percentage || 0, color: '#10b981' },
        { label: 'Deep 2', value: shotData.deep_2?.percentage || 0, color: '#F9423A' },
        { label: 'Short 2', value: shotData.short_2?.percentage || 0, color: '#6b7280' },
        { label: 'Long 2', value: shotData.long_2?.percentage || 0, color: '#3b82f6' }
    ];
    
    // Calculate total and convert to radians
    const total = segments.reduce((sum, seg) => sum + seg.value, 0);
    let currentAngle = 0;
    
    // Animate pie chart drawing
    let progress = 0;
    const duration = 2000;
    const startTime = Date.now();
    
    function drawPieChart() {
        const elapsed = Date.now() - startTime;
        progress = Math.min(elapsed / duration, 1);
        
        // Clear canvas
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        // Draw segments
        let angle = 0;
        segments.forEach((segment, index) => {
            const segmentAngle = (segment.value / total) * 2 * Math.PI * progress;
            
            ctx.beginPath();
            ctx.moveTo(centerX, centerY);
            ctx.arc(centerX, centerY, radius, angle, angle + segmentAngle);
            ctx.closePath();
            
            ctx.fillStyle = segment.color;
            ctx.fill();
            
            // Add glow effect
            ctx.shadowBlur = 15;
            ctx.shadowColor = segment.color;
            ctx.fill();
            ctx.shadowBlur = 0;
            
            angle += segmentAngle;
        });
        
        // Continue animation
        if (progress < 1) {
            requestAnimationFrame(drawPieChart);
        }
    }
    
    setTimeout(() => {
        drawPieChart();
    }, 2500);
}

/**
 * Animate number counter
 */
function animateCounter(element, start, end, duration) {
    if (!element) return;
    
    const startTime = Date.now();
    const range = end - start;
    
    function updateCounter() {
        const elapsed = Date.now() - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        // Easing function (easeOutCubic)
        const eased = 1 - Math.pow(1 - progress, 3);
        const current = start + (range * eased);
        
        element.textContent = current.toFixed(1);
        
        if (progress < 1) {
            requestAnimationFrame(updateCounter);
        } else {
            element.textContent = end.toFixed(1);
        }
    }
    
    updateCounter();
}

/**
 * Handle file upload for scorecard generation
 */
document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('scorecardUploadForm');
    
    if (uploadForm) {
        uploadForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const fileInput = document.getElementById('scorecardFile');
            const file = fileInput.files[0];
            
            if (!file) {
                alert('Please select a file');
                return;
            }
            
            const uploadBtn = document.getElementById('uploadBtn');
            uploadBtn.disabled = true;
            uploadBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';
            
            try {
                // Upload file to smartdash endpoint (reuse existing upload)
                const formData = new FormData();
                formData.append('file', file);
                
                const response = await fetch('/smartdash-upload', {
                    method: 'POST',
                    body: formData
                });
                
                if (response.ok) {
                    // Redirect to results or reload
                    window.location.reload();
                } else {
                    throw new Error('Upload failed');
                }
            } catch (error) {
                console.error('Error uploading file:', error);
                alert('Error processing file. Please try again.');
                uploadBtn.disabled = false;
                uploadBtn.innerHTML = '<i class="fas fa-chart-bar me-2"></i>Generate Scorecard';
            }
        });
    }
    
    // Add entrance animation class to main scorecard
    const scorecardMain = document.getElementById('scorecardMain');
    if (scorecardMain) {
        scorecardMain.classList.add('animate-entrance');
    }
    
    // Add glow pulse to sections
    const sections = document.querySelectorAll('.section');
    sections.forEach((section, index) => {
        setTimeout(() => {
            section.style.animation = 'pulse 3s ease-in-out infinite';
        }, 3000 + (index * 200));
    });
});

/**
 * Utility: Easing functions
 */
const Easing = {
    easeInOutCubic: (t) => t < 0.5 ? 4 * t * t * t : (t - 1) * (2 * t - 2) * (2 * t - 2) + 1,
    easeOutBack: (t) => {
        const c1 = 1.70158;
        const c3 = c1 + 1;
        return 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2);
    },
    easeOutElastic: (t) => {
        const c4 = (2 * Math.PI) / 3;
        return t === 0 ? 0 : t === 1 ? 1 : Math.pow(2, -10 * t) * Math.sin((t * 10 - 0.75) * c4) + 1;
    }
};

/**
 * Add hover effects to circular indicators
 */
document.addEventListener('DOMContentLoaded', function() {
    const circularMetrics = document.querySelectorAll('.circular-metric');
    
    circularMetrics.forEach(metric => {
        metric.addEventListener('mouseenter', function() {
            const circle = this.querySelector('.progress-ring-circle');
            if (circle) {
                circle.style.filter = 'drop-shadow(0 0 20px rgba(249, 66, 58, 1))';
                circle.style.strokeWidth = '10';
            }
        });
        
        metric.addEventListener('mouseleave', function() {
            const circle = this.querySelector('.progress-ring-circle');
            if (circle) {
                circle.style.filter = 'drop-shadow(0 0 8px rgba(249, 66, 58, 0.6))';
                circle.style.strokeWidth = '8';
            }
        });
    });
});

/**
 * Parallax effect on scroll
 */
window.addEventListener('scroll', function() {
    const scrolled = window.pageYOffset;
    const sections = document.querySelectorAll('.section');
    
    sections.forEach((section, index) => {
        const speed = 0.5 + (index * 0.1);
        const yPos = -(scrolled * speed);
        section.style.transform = `translateY(${yPos}px)`;
    });
});

/**
 * Export functions for external use
 */
window.initializeAnimatedScorecard = initializeAnimatedScorecard;
window.animateCircularIndicators = animateCircularIndicators;
window.animateHorizontalBars = animateHorizontalBars;
window.animateShotDistribution = animateShotDistribution;

console.log('Animated Scorecard JS loaded successfully');

