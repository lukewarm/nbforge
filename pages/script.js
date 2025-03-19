document.addEventListener('DOMContentLoaded', function() {
    // Initialize the challenge cards
    initChallengeSolutions();
    
    // Initialize placeholder images
    initPlaceholderImages();
    
    // Mobile menu toggle
    const mobileMenuButton = document.getElementById('mobile-menu-button');
    const navLinks = document.querySelector('.nav-links');
    
    if (mobileMenuButton) {
        mobileMenuButton.addEventListener('click', function() {
            navLinks.classList.toggle('active');
        });
    }
    
    // Pain Points section interactivity
    const challengeCards = document.querySelectorAll('.challenge-card');
    const solutionDetails = document.querySelectorAll('.solution-detail');
    
    // Set default active card
    if (challengeCards.length > 0 && solutionDetails.length > 0) {
        challengeCards[0].classList.add('active');
        solutionDetails[0].classList.remove('hidden');
    }
    
    // Add click handlers to cards
    challengeCards.forEach((card, index) => {
        card.addEventListener('click', () => {
            // Remove active class from all cards
            challengeCards.forEach(c => c.classList.remove('active'));
            
            // Add active class to clicked card
            card.classList.add('active');
            
            // Hide all solution details
            solutionDetails.forEach(detail => detail.classList.add('hidden'));
            
            // Show the corresponding solution detail
            if (solutionDetails[index]) {
                solutionDetails[index].classList.remove('hidden');
            }
            
            // Scroll to solution if on mobile
            if (window.innerWidth < 768) {
                const solutionsContainer = document.querySelector('.solutions-container');
                if (solutionsContainer) {
                    solutionsContainer.scrollIntoView({ behavior: 'smooth' });
                }
            }
        });
    });
    
    // Add smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
                
                // Close mobile menu if open
                if (navLinks.classList.contains('active')) {
                    navLinks.classList.remove('active');
                }
            }
        });
    });
    
    // Add animation for elements when they come into view
    const animateElements = document.querySelectorAll('.feature-card, .challenge-card, .solution-detail, .contact-card');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
                observer.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.2
    });
    
    animateElements.forEach(el => {
        observer.observe(el);
        // Add initial hidden state via class
        el.classList.add('pre-animation');
    });
    
    // Add CSS for animations
    const style = document.createElement('style');
    style.innerHTML = `
        .pre-animation {
            opacity: 0;
            transform: translateY(20px);
            transition: opacity 0.6s ease-out, transform 0.6s ease-out;
        }
        
        .animate-in {
            opacity: 1;
            transform: translateY(0);
        }
    `;
    document.head.appendChild(style);
});

function initChallengeSolutions() {
    const challengeCards = document.querySelectorAll('.challenge-card');
    const solutionDetails = document.querySelectorAll('.solution-detail');
    
    // Show the first solution by default
    if (solutionDetails.length > 0) {
        solutionDetails[0].classList.remove('hidden');
    }
    
    // Add click event to each challenge card
    challengeCards.forEach(card => {
        card.addEventListener('click', function() {
            // Get the target solution
            const targetId = this.getAttribute('data-target');
            const targetSolution = document.getElementById(targetId);
            
            // Hide all solutions
            solutionDetails.forEach(solution => {
                solution.classList.add('hidden');
            });
            
            // Remove active class from all cards
            challengeCards.forEach(c => {
                c.classList.remove('active');
            });
            
            // Show the target solution and set this card as active
            if (targetSolution) {
                targetSolution.classList.remove('hidden');
                this.classList.add('active');
                
                // Smooth scroll to the solution if on mobile
                if (window.innerWidth < 768) {
                    targetSolution.scrollIntoView({ behavior: 'smooth' });
                }
            }
        });
    });
}

function initPlaceholderImages() {
    const placeholderImages = document.querySelectorAll('.placeholder-image');
    
    placeholderImages.forEach(image => {
        // Add text inside the placeholder
        const altText = image.getAttribute('alt');
        image.textContent = `[${altText}]`;
    });
}

// Simple analytics tracking
function trackEvent(category, action, label) {
    if (typeof gtag !== 'undefined') {
        gtag('event', action, {
            'event_category': category,
            'event_label': label
        });
    }
}

// Track outbound links
document.addEventListener('click', function(e) {
    const target = e.target.closest('a');
    if (target && target.hostname !== window.location.hostname) {
        trackEvent('Outbound Link', 'click', target.href);
    }
});

// Track GitHub and Demo clicks
document.querySelectorAll('a[href*="github.com"], a[href*="demo.nbforge.com"]').forEach(link => {
    link.addEventListener('click', function() {
        const isGithub = this.href.includes('github.com');
        trackEvent('CTA', 'click', isGithub ? 'GitHub' : 'Demo');
    });
}); 