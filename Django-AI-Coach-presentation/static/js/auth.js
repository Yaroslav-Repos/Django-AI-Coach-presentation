/*
 * AuthManager єю
 */

class AuthManager {
    static refreshInterval = null;
    static redirectInProgress = false; 

    static async verifyAuthOnBackend() {
        try {
            const res = await fetch('/api/auth/verify/', {
                credentials: 'include'  
            });
            const isValid = res.ok;
            console.log(`Auth check: ${isValid ? 'VALID' : 'INVALID'}`);
            return isValid;
        } catch (e) {
            console.error('Auth verification failed:', e);
            return false;
        }
    }


    static redirectToLogin() {
        if (AuthManager.redirectInProgress) {
            console.warn('Redirect already in progress');
            return;
        }
        AuthManager.redirectInProgress = true;
        console.warn('Redirecting to login...');
        window.location.href = '/login/';
    }


    static async silentRefresh() {
        try {
            const res = await fetch('/api/token/refresh/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include'
            });
            if (res.ok) {
                console.log('Token refreshed');
                return true;
            }
        } catch (e) {
            console.error('Token refresh failed:', e);
        }
        return false;
    }


    static async fetchWithAuth(url, options = {}) {
        const headers = { ...options.headers };
        
        let response = await fetch(url, {
            ...options,
            headers,
            credentials: 'include'
        });

       
        if (response.status === 401) {
            const refreshed = await this.silentRefresh();
            if (refreshed) {
                response = await fetch(url, {
                    ...options,
                    headers,
                    credentials: 'include'
                });
            } else {
                this.redirectToLogin();
                return null;
            }
        }
        return response;
    }


    static startAutoRefresh(intervalMinutes = 10) {
        if (this.refreshInterval) clearInterval(this.refreshInterval);

        this.refreshInterval = setInterval(async () => {
            console.log('Auto-refresh check...');
            const isValid = await this.verifyAuthOnBackend();
            if (!isValid) {
                console.warn('Auth expired');
                this.stopAutoRefresh();
                this.redirectToLogin();
            } else {
                await this.silentRefresh();
            }
        }, intervalMinutes * 60 * 1000);

        console.log(`Auto-refresh started (every ${intervalMinutes} min)`);
    }


    static stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
            console.log('Auto-refresh stopped');
        }
    }


    static async logout() {
        try {
            const res = await fetch('/api/auth/logout/', {
                method: 'POST',
                credentials: 'include'
            });
            if (res.ok) {
                console.log('Logout successful');
            }
        } catch (e) {
            console.error('Logout error:', e);
        }

        this.stopAutoRefresh();
        this.redirectToLogin();
    }


    static async ensureAuthenticated() {
        console.log('Verifying authentication...');
        const isAuth = await this.verifyAuthOnBackend();
        if (!isAuth) {
            console.warn('Not authenticated - redirecting');
            this.redirectToLogin();
            return false;
        }
        console.log('Authenticated');
        return true;
    }
}

