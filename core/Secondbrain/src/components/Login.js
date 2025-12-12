import React from 'react';
import { signIn } from '../auth';

function Login() {
  return (
    <div className="login-overlay">
      <div className="login-card">
        <img src="oberaconnect-logo.png" alt="OberaConnect" className="login-logo" onError={(e) => e.target.style.display = 'none'} />
        <h1 className="login-title">Engineering Command Center</h1>
        <p className="login-subtitle">Sign in with your OberaConnect account to continue</p>
        <button className="login-btn" id="loginBtn" onClick={signIn}>
          <svg width="20" height="20" viewBox="0 0 21 21" fill="none"><path d="M10 0H0V10H10V0Z" fill="#F25022" /><path d="M21 0H11V10H21V0Z" fill="#7FBA00" /><path d="M10 11H0V21H10V11Z" fill="#00A4EF" /><path d="M21 11H11V21H21V11Z" fill="#FFB900" /></svg>
          Sign in with Microsoft
        </button>
        <div className="login-error" id="loginError"></div>
      </div>
    </div>
  );
}

export default Login;