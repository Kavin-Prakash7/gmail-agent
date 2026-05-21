class UIManager {
    constructor() {
        this.emailsList = document.getElementById('emailsList');
        this.insightsContent = document.getElementById('insightsContent');
        this.loginBtn = document.getElementById('loginBtn');
        this.syncIndicator = document.getElementById('syncIndicator');
        this.gmailStatus = document.getElementById('gmailStatus');
        
        this.detailSection = document.getElementById('detailSection');
        this.insightsSection = document.getElementById('insightsSection');
        this.detailSubject = document.getElementById('detailSubject');
        this.detailSender = document.getElementById('detailSender');
        this.detailTime = document.getElementById('detailTime');
        this.detailContent = document.getElementById('detailContent');
        this.closeDetail = document.getElementById('closeDetail');
        this.insightsTitle = document.getElementById('insightsTitle');

        this.closeDetail.addEventListener('click', () => this.hideDetail());
    }

    renderSkeletons(count = 4) {
        this.emailsList.innerHTML = '';
        for (let i = 0; i < count; i++) {
            const skel = document.createElement('div');
            skel.className = 'skeleton-card skeleton';
            this.emailsList.appendChild(skel);
        }
    }

    renderDetailSkeleton() {
        this.detailSubject.innerHTML = '<span class="ai-glow-text">Orchestrating...</span>';
        this.detailSender.textContent = '';
        this.detailTime.textContent = '';
        
        this.detailContent.innerHTML = `
            <div class="orchestration-timeline">
                <div class="timeline-step" id="step-parse"><i class="fa-solid fa-envelope-open-text"></i> Email Body Parsed</div>
                <div class="timeline-step" id="step-meta"><i class="fa-solid fa-fingerprint"></i> Metadata Extracted</div>
                <div class="timeline-step" id="step-intent"><i class="fa-solid fa-brain"></i> Intent Classified</div>
                <div class="timeline-step" id="step-summary"><i class="fa-solid fa-bolt"></i> Gemini Intelligence Generated</div>
                <div class="timeline-step" id="step-opp"><i class="fa-solid fa-magnifying-glass-chart"></i> Opportunity Detection Complete</div>
                <div class="timeline-step" id="step-action"><i class="fa-solid fa-wand-magic-sparkles"></i> Recommended Actions Ready</div>
            </div>
        `;
        
        const steps = ['step-parse', 'step-meta', 'step-intent', 'step-summary', 'step-opp', 'step-action'];
        steps.forEach((step, index) => {
            setTimeout(() => {
                const el = document.getElementById(step);
                if (el) el.classList.add('active');
            }, index * 600); 
        });
    }

    renderEmails(emails, activeId = null) {
        this.emailsList.innerHTML = '';
        if (emails.length === 0) {
            this.emailsList.innerHTML = '<p class="empty-state">No new emails.</p>';
            return;
        }

        emails.forEach(email => {
            const initial = email.sender.charAt(0).toUpperCase();
            const card = document.createElement('div');
            card.className = `email-card ${email.id === activeId ? 'active' : ''}`;
            card.dataset.id = email.id;
            
            let tagsHtml = email.tags.map(tag => `<span class="tag ai-tag"><i class="fa-solid fa-sparkles"></i> ${tag}</span>`).join('');
            
            const aiSummaryHtml = email.ai_summary ? `
                <div class="email-ai-summary" style="margin-top: 0.75rem; font-size: 0.8rem; color: #93c5fd; background: rgba(59, 130, 246, 0.1); padding: 0.5rem; border-radius: 6px; border-left: 2px solid var(--accent-color);">
                    <i class="fa-solid fa-robot"></i> <strong>AI Summary:</strong> ${email.ai_summary}
                </div>` : '';

            card.innerHTML = `
                <div class="email-header">
                    <div class="sender-info">
                        <div class="sender-avatar">${initial}</div>
                        <span class="sender-name">${email.sender}</span>
                    </div>
                    <span class="email-time">${email.time}</span>
                </div>
                <div class="email-subject">${email.subject}</div>
                <div class="email-snippet">${email.snippet}</div>
                ${aiSummaryHtml}
                <div class="email-tags">${tagsHtml}</div>
            `;
            
            this.emailsList.appendChild(card);
        });
    }

    showDetail(email) {
        this.detailSection.classList.remove('hidden');
        this.insightsSection.classList.add('hidden'); 
        
        this.detailSubject.textContent = email.subject;
        this.detailSender.textContent = `From: ${email.sender}`;
        this.detailTime.textContent = email.timestamp;
        
        let bodyHtml = email.body || email.snippet;
        if (!bodyHtml.includes('<html') && !bodyHtml.includes('<div')) {
            bodyHtml = `<div style="white-space: pre-wrap; font-family: 'Inter', sans-serif;">${bodyHtml}</div>`;
        }
        this.detailContent.innerHTML = bodyHtml;

        this.renderEmailIntelligence(email.ai_analysis);

        document.querySelectorAll('.email-card').forEach(c => c.classList.remove('active'));
        const activeCard = document.querySelector(`.email-card[data-id="${email.id}"]`);
        if (activeCard) activeCard.classList.add('active');
    }

    hideDetail() {
        this.detailSection.classList.add('hidden');
        this.insightsSection.classList.remove('hidden');
        document.querySelectorAll('.email-card').forEach(c => c.classList.remove('active'));
    }

    renderEmailIntelligence(analysis) {
        if (!analysis) return;

        this.insightsSection.classList.remove('hidden');
        this.insightsTitle.innerHTML = `<span class="ai-glow-text"><i class="fa-solid fa-network-wired"></i> AI Orchestration</span>`;
        
        const urgencyColor = analysis.urgency ? analysis.urgency.toLowerCase() : 'low';
        
        const trustHtml = `
            <div class="metric-ring">
                <svg viewBox="0 0 36 36" class="circular-chart ${analysis.trust_score > 80 ? 'green' : 'orange'}">
                    <path class="circle-bg" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"/>
                    <path class="circle" stroke-dasharray="${analysis.trust_score}, 100" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"/>
                    <text x="18" y="20.35" class="percentage">${analysis.trust_score}%</text>
                </svg>
                <span>Trust</span>
            </div>
        `;
        
        const confHtml = `
            <div class="metric-ring">
                <svg viewBox="0 0 36 36" class="circular-chart blue">
                    <path class="circle-bg" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"/>
                    <path class="circle" stroke-dasharray="${analysis.confidence_score}, 100" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"/>
                    <text x="18" y="20.35" class="percentage">${analysis.confidence_score}%</text>
                </svg>
                <span>Confidence</span>
            </div>
        `;

        const actionIcons = {
            'draft_reply': 'fa-pen-to-square',
            'archive': 'fa-box-archive',
            'mark_important': 'fa-star',
            'reminder': 'fa-bell',
            'task': 'fa-list-check',
            'calendar': 'fa-calendar-plus',
            'auto_categorize': 'fa-tags'
        };

        const actionsHtml = (analysis.action_items || []).map(a => {
            const icon = actionIcons[a.type] || 'fa-bolt';
            return `
            <div class="action-item-card">
                <div class="action-icon"><i class="fa-solid ${icon}"></i></div>
                <div class="action-info">
                    <h5>${a.action}</h5>
                    <span>${a.context}</span>
                </div>
                <button class="icon-btn execute-btn"><i class="fa-solid fa-play"></i></button>
            </div>
            `;
        }).join('');

        const oppsHtml = (analysis.opportunities || []).map(o => `<li><i class="fa-solid fa-check text-green"></i> ${o}</li>`).join('');
        const tags = analysis.smart_tags || [];

        this.insightsContent.innerHTML = `
            <div class="ai-panel-glass">
                <div class="ai-panel-header">
                    <h4><i class="fa-solid fa-microchip"></i> Executive Summary</h4>
                    <span class="urgency-badge ${urgencyColor}">${analysis.urgency}</span>
                </div>
                <p class="ai-summary-text">${analysis.summary}</p>
                <div class="ai-metrics-row">
                    ${trustHtml}
                    ${confHtml}
                    <div class="tone-badge">
                        <i class="fa-solid fa-comment-dots"></i> ${analysis.tone}
                    </div>
                </div>
                <div class="smart-tags-container">
                    ${tags.map(t => `<span class="smart-tag">#${t}</span>`).join('')}
                </div>
            </div>

            <div class="ai-panel-glass intent-panel">
                <div class="ai-panel-header">
                    <h4><i class="fa-solid fa-bullseye"></i> Intent & Reasoning</h4>
                    <span class="category-badge">${analysis.category}</span>
                </div>
                <div class="reasoning-box">
                    <p><strong>Intent:</strong> ${analysis.intent}</p>
                    <p class="reasoning-text"><i class="fa-solid fa-code-branch"></i> ${analysis.reasoning}</p>
                </div>
                ${oppsHtml ? `<ul class="opportunities-list">${oppsHtml}</ul>` : ''}
            </div>

            <div class="ai-panel-glass actions-panel">
                <div class="ai-panel-header">
                    <h4><i class="fa-solid fa-wand-magic-sparkles"></i> Recommended Actions</h4>
                </div>
                <div class="actions-list">
                    ${actionsHtml || '<p class="text-muted" style="font-size: 0.8rem; text-align: center;">No automated actions required.</p>'}
                </div>
            </div>
        `;
    }

    renderInsights(insights) {
        this.insightsTitle.textContent = "AI Orchestration";
        this.insightsContent.innerHTML = '';
        if (!insights || insights.length === 0) {
            this.insightsContent.innerHTML = '<p class="empty-state">No active insights.</p>';
            return;
        }
        
        insights.forEach(insight => {
            const card = document.createElement('div');
            card.className = `insight-card ${insight.type}`;
            const icon = insight.type === 'opportunity' ? 'fa-star' : 'fa-triangle-exclamation';

            card.innerHTML = `
                <i class="fa-solid ${icon}"></i>
                <div>
                    <h4>${insight.title}</h4>
                    <p>${insight.desc}</p>
                    ${insight.action ? `<button class="action-btn small">${insight.action}</button>` : ''}
                </div>
            `;
            this.insightsContent.appendChild(card);
        });
    }

    setLoggedInState() {
        this.loginBtn.innerHTML = '<i class="fa-brands fa-google"></i> Connected';
        this.loginBtn.style.background = 'var(--success)';
        this.gmailStatus.nextElementSibling.textContent = 'Gmail Synced';
        this.gmailStatus.style.backgroundColor = 'var(--success)';
        this.gmailStatus.style.boxShadow = '0 0 8px var(--success)';
        this.syncIndicator.classList.remove('hidden');
    }
}
