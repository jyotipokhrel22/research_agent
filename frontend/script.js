document.addEventListener('DOMContentLoaded', () => {

    // Intersection Observer for scroll animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: "0px 0px -50px 0px"
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                observer.unobserve(entry.target); // Stop observing once visible
            }
        });
    }, observerOptions);

    // Observe all fade-in elements
    document.querySelectorAll('.fade-in').forEach(element => {
        observer.observe(element);
    });

    // App Navigation Logic
    const getStartedBtn = document.getElementById('get-started-btn');
    const landingPage = document.getElementById('landing-page');
    const appContainer = document.getElementById('app-container');

    if (getStartedBtn && landingPage && appContainer) {
        getStartedBtn.addEventListener('click', () => {
            landingPage.classList.add('hidden');
            appContainer.classList.remove('hidden');
            setTimeout(() => {
                window.scrollTo(0, 0);
                const mainPrompt = document.getElementById('main-prompt');
                if (mainPrompt) mainPrompt.focus();
            }, 50);
        });
    }

    // App Sidebar Toggle
    const openSidebarBtn = document.getElementById('open-sidebar');
    const closeSidebarBtn = document.getElementById('close-sidebar');
    const appSidebar = document.getElementById('app-sidebar');

    if (openSidebarBtn && closeSidebarBtn && appSidebar) {
        openSidebarBtn.addEventListener('click', () => {
            appSidebar.classList.remove('collapsed');
        });

        closeSidebarBtn.addEventListener('click', () => {
            appSidebar.classList.add('collapsed');
        });

        if (window.innerWidth <= 768) {
            appSidebar.classList.add('collapsed');
        }
    }

    // Run Query Logic (Perplexity Theme)
    const runPxQueryBtn = document.getElementById('run-px-query');
    const initialView = document.getElementById('initial-view');
    const threadView = document.getElementById('thread-view');
    const mainPrompt = document.getElementById('main-prompt');

    if (runPxQueryBtn && initialView && threadView) {
        runPxQueryBtn.addEventListener('click', () => {
            if (mainPrompt && mainPrompt.value.trim() === '') {
                mainPrompt.value = "Explainable AI research gaps";
            }
            initialView.style.display = 'none';
            threadView.classList.remove('hidden');
        });
    }
    // Theme Toggle Logic
    const themeToggles = document.querySelectorAll('.theme-toggle-btn');

    const currentTheme = localStorage.getItem('theme') || 'dark';
    document.documentElement.setAttribute('data-theme', currentTheme);
    updateIcons(currentTheme);

    themeToggles.forEach(toggle => {
        toggle.addEventListener('click', () => {
            const theme = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
            document.documentElement.setAttribute('data-theme', theme);
            localStorage.setItem('theme', theme);
            updateIcons(theme);
        });
    });

    function updateIcons(theme) {
        const sunIcons = document.querySelectorAll('.sun-icon');
        const moonIcons = document.querySelectorAll('.moon-icon');

        if (theme === 'light') {
            sunIcons.forEach(icon => icon.classList.add('hidden'));
            moonIcons.forEach(icon => icon.classList.remove('hidden'));
        } else {
            sunIcons.forEach(icon => icon.classList.remove('hidden'));
            moonIcons.forEach(icon => icon.classList.add('hidden'));
        }
    }
});
