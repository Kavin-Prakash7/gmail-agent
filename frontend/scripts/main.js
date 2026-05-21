document.addEventListener('DOMContentLoaded', async () => {
    const ui = new UIManager();
    let currentEmails = [];
    
    ApiService.checkHealth().then(health => {
        if (health) console.log('Backend connected:', health);
    });

    try {
        const ws = new WebSocket('ws://localhost:8000/ws/dashboard_client');
        ws.onmessage = (event) => {
            console.log("Realtime Update:", event.data);
        };
    } catch (e) {
        console.log("WebSocket connection failed");
    }

    const urlParams = new URLSearchParams(window.location.search);
    let token = urlParams.get('token');
    
    if (token) {
        localStorage.setItem('gmail_token', token);
        window.history.replaceState({}, document.title, "/");
    } else {
        token = localStorage.getItem('gmail_token');
    }

    if (token) {
        ui.renderSkeletons(4);
        ui.setLoggedInState();
        loadDashboard(token);
    }

    async function loadDashboard(token) {
        try {
            const [emails, insights] = await Promise.all([
                ApiService.getEmails(token),
                ApiService.getInsights(token)
            ]);
            currentEmails = emails;
            ui.renderEmails(emails);
            // ui.renderInsights(insights); // Insights are now replaced by deep orchestration
        } catch (e) {
            console.error("Session error:", e);
            handleLogout();
        }
    }

    function handleLogout() {
        localStorage.removeItem('gmail_token');
        window.location.href = "/";
    }

    // Global click listener for email cards
    document.addEventListener('click', async (e) => {
        const card = e.target.closest('.email-card');
        if (card) {
            const emailId = card.dataset.id;
            const token = localStorage.getItem('gmail_token');
            
            ui.detailSection.classList.remove('hidden');
            ui.insightsSection.classList.add('hidden');
            ui.renderDetailSkeleton();

            try {
                const detail = await ApiService.getEmailDetail(emailId, token);
                ui.showDetail(detail);
            } catch (err) {
                console.error("Failed to load email detail", err);
                ui.detailContent.innerHTML = `<p class="empty-state">Failed to orchestrate email details.</p>`;
            }
        }
    });

    document.getElementById('loginBtn').addEventListener('click', () => {
        if (!localStorage.getItem('gmail_token')) {
            window.location.href = 'http://localhost:8000/auth/google/login';
        }
    });
});
