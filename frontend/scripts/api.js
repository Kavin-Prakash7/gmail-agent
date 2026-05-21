const API_BASE = "http://localhost:8000";

class ApiService {
    static async checkHealth() {
        try {
            const res = await fetch(`${API_BASE}/api/health`);
            return await res.json();
        } catch (e) {
            console.warn("Backend not reachable.");
            return null;
        }
    }

    static async getEmails(token) {
        if (!token) return [];
        try {
            const res = await fetch(`${API_BASE}/api/emails/latest?token=${token}`);
            if (!res.ok) {
                if (res.status === 401) throw new Error("Unauthorized");
                throw new Error("Failed to fetch");
            }
            const data = await res.json();
            return data.emails || [];
        } catch (e) {
            console.error("Error fetching emails:", e);
            throw e;
        }
    }

    static async getEmailDetail(id, token) {
        if (!token) return null;
        try {
            const res = await fetch(`${API_BASE}/api/emails/${id}?token=${token}`);
            if (!res.ok) throw new Error("Failed to fetch detail");
            return await res.json();
        } catch (e) {
            console.error("Error fetching email detail:", e);
            throw e;
        }
    }

    static async getInsights(token) {
        if (!token) return [];
        try {
            const res = await fetch(`${API_BASE}/api/insights?token=${token}`);
            if (!res.ok) return [];
            const data = await res.json();
            return data.insights || [];
        } catch (e) {
            console.error("Error fetching insights:", e);
            return [];
        }
    }
}
