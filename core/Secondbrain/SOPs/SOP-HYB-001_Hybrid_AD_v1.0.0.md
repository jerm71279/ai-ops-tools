# SOP-HYB-001: Hybrid Active Directory Major Components

**Version:** 1.0
**Status:** Final
**Author:** OberaConnect IT
**Date:** 2025-12-02

---

## 1.0 Purpose

The purpose of this Standard Operating Procedure (SOP) is to document the major components of the Setco Hybrid Active Directory (AD) environment, which integrates the on-premises Windows Active Directory with Microsoft 365 (M365).

## 2.0 Scope

This SOP applies to the management and troubleshooting of the core infrastructure that enables the hybrid AD functionality for Setco. This includes the AD Sync service, Active Directory Federation Services (ADFS), and related DNS configurations.

## 3.0 Prerequisites

-   Basic understanding of Windows Server Active Directory.
-   Familiarity with Microsoft 365 administration.
-   Knowledge of DNS principles and management.

## 4.0 Procedure

### 4.1 Setco-DC01: Active Directory Sync Service

1.  **Component:** `Setco-DC01`
2.  **Role:** Active Directory domain controller responsible for synchronizing user accounts and passwords from the on-premises Windows Active Directory to M365.
3.  **Service Name:** The synchronization service is named `Microsoft Azure AD Sync`.
4.  **Sync Direction:** The synchronization is one-way, from the on-premises AD to M365.
    *   **Important:** Accounts created directly in M365 will not be synchronized back to the on-premises Active Directory.
5.  **Troubleshooting:** If the AD Sync is not updating correctly, the first step is to attempt a restart of the `Microsoft Azure AD Sync` service on `Setco-DC01`.

### 4.2 Setco-ADFS01: Active Directory Federation Services

1.  **Component:** `Setco-ADFS01`
2.  **Role:** Provides secure, authenticated access to resources for domain-joined devices, web applications, and other systems within the organization's AD, as well as approved third-party systems.
3.  **Authentication Flow:** M365 communicates with the on-premises AD environment through the ADFS services for authentication purposes.

### 4.3 Setco DNS Settings: Authentication Discovery

1.  **Mechanism:** Microsoft's authentication services locate the on-premises ADFS server by querying public DNS records for the domain (`setcoservices.com`).
2.  **DNS Record:** The key record is an `A` record with the name `externalvalidation`.
3.  **Configuration:** The `externalvalidation.setcoservices.com` `A` record must be set to the external IP address of the ADFS server (`Setco-ADFS01`).
4.  **Authentication Process:**
    *   A user attempts to log in to a Microsoft service.
    *   Microsoft's authenticator identifies the user's domain (e.g., `setcoservices.com`).
    *   It then looks for the `externalvalidation` `A` record for that domain.
    *   Authentication requests are directed to the IP address specified in that record, which is the ADFS server. The IP address itself is configured in Azure.

## 5.0 Verification

1.  **AD Sync Health:** Check the synchronization status in the Microsoft 365 admin center to ensure that the last sync was successful and recent.
2.  **M365 Login:** Have a test user attempt to log in to the M365 portal. A successful login that redirects to the organization's ADFS login page and then back to M365 confirms that the ADFS and DNS configuration is working.

## 6.0 Additional Considerations

-   Any changes to the external IP address of the `Setco-ADFS01` server must be reflected in the `externalvalidation.setcoservices.com` DNS `A` record to avoid authentication failures.
-   The `Microsoft Azure AD Sync` service should be monitored for any stoppage or errors, as this will prevent password and user object changes from being reflected in M365.
