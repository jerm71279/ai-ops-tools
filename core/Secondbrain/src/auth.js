import { PublicClientApplication } from "@azure/msal-browser";

export const msalConfig = {
    auth: {
        clientId: '2527689c-fd5b-47d6-820c-45e4157f9a4f',
        authority: 'https://login.microsoftonline.com/ad6cfe8e-bf9d-4bb0-bfd7-05058c2c69dd',
        redirectUri: window.location.origin,
        postLogoutRedirectUri: window.location.origin
    },
    cache: {
        cacheLocation: 'sessionStorage',
        storeAuthStateInCookie: false
    }
};

export const loginRequest = {
    scopes: ['User.Read', 'Sites.ReadWrite.All']
};

export const msalInstance = new PublicClientApplication(msalConfig);

export async function initializeMsal() {
    try {
        await msalInstance.initialize();
        const response = await msalInstance.handleRedirectPromise();
        if (response) {
            return handleLoginResponse(response);
        } else {
            const accounts = msalInstance.getAllAccounts();
            if (accounts.length > 0) {
                return silentLogin(accounts[0]);
            }
        }
    } catch (error) {
        console.error('MSAL initialization error:', error);
        showLoginError('Failed to initialize authentication');
    }
}

export async function signIn() {
    const btn = document.getElementById('loginBtn');
    btn.disabled = true;
    btn.innerHTML = '<span>Signing in...</span>';

    try {
        await msalInstance.loginRedirect(loginRequest);
    } catch (error) {
        console.error('Login error:', error);
        showLoginError('Sign in failed. Please try again.');
        btn.disabled = false;
        btn.innerHTML = '<svg width="20" height="20" viewBox="0 0 21 21" fill="none"><path d="M10 0H0V10H10V0Z" fill="#F25022"/><path d="M21 0H11V10H21V0Z" fill="#7FBA00"/><path d="M10 11H0V21H10V11Z" fill="#00A4EF"/><path d="M21 11H11V21H21V11Z" fill="#FFB900"/></svg> Sign in with Microsoft';
    }
}

async function silentLogin(account) {
    try {
        const response = await msalInstance.acquireTokenSilent({
            ...loginRequest,
            account: account
        });
        return handleLoginResponse(response);
    } catch (error) {
        console.log('Silent login failed, showing login screen');
    }
}

async function handleLoginResponse(response) {
    if (!response || !response.account) return;

    const userEmail = response.account.username.toLowerCase();

    // Engineering team - allowed users
    const allowedEmails = [
        'mavrick.faison@oberaconnect.com',
        'patrick.mcfarland@oberaconnect.com',
        'robbie.mcfarland@oberaconnect.com',
        'jim.boudreaux@oberaconnect.com',
        'samuel.blake@oberaconnect.com',
        'jeremy.smith@oberaconnect.com',
        'philip.durant@oberaconnect.com'
    ];

    // Also allow any @oberaconnect.com domain for team flexibility
    const isOberaUser = userEmail.endsWith('@oberaconnect.com');

    if (!isOberaUser && !allowedEmails.includes(userEmail)) {
        showLoginError(`Access denied. ${response.account.name} is not authorized to use this application.`);
        await msalInstance.logoutRedirect();
        return;
    }

    return {
        isAuthenticated: true,
        accessToken: response.accessToken,
        currentUser: {
            displayName: response.account.name,
            mail: response.account.username
        }
    };
}

export async function signOut() {
    if (msalInstance) {
        await msalInstance.logoutRedirect();
    }
}

export async function getAccessToken() {
    if (!msalInstance) return null;

    const accounts = msalInstance.getAllAccounts();
    if (accounts.length === 0) return null;

    try {
        const response = await msalInstance.acquireTokenSilent({
            ...loginRequest,
            account: accounts[0],
            forceRefresh: false
        });
        return response.accessToken;
    } catch (error) {
        console.error('Token refresh error, attempting interactive:', error);
        // If silent fails (token expired), try interactive
        try {
            const response = await msalInstance.acquireTokenPopup({
                ...loginRequest,
                account: accounts[0]
            });
            return response.accessToken;
        } catch (interactiveError) {
            console.error('Interactive token acquisition failed:', interactiveError);
            // Force re-login
            await msalInstance.loginRedirect(loginRequest);
            return null;
        }
    }
}

function showLoginError(message) {
    const errorEl = document.getElementById('loginError');
    errorEl.textContent = message;
    errorEl.classList.add('show');
}
