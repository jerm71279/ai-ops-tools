Loaded cached credentials.
```markdown
# Standard Operating Procedure: SOP-NET-004

**Title:** Register Device in MySonicwall
**Version:** 1.0
**Author:** Gemini
**Date:** 2025-12-02

---

## 1.0 Purpose

To provide a standardized procedure for registering a new SonicWall device in the MySonicwall portal, ensuring it is correctly associated with a tenant and ready for management.

## 2.0 Scope

This procedure applies to all IT personnel and network administrators responsible for the deployment and initial configuration of new SonicWall hardware.

## 3.0 Prerequisites

-   **Credentials:** You must have valid login credentials for the [MySonicwall portal](https://www.mysonicwall.com).
-   **Device Information:** You must have the **Serial Number** and **Activation Code** for the SonicWall device. This information is typically found on the original packaging or on a sticker on the device itself.
-   **Tenant Information:** You must know the name of the tenant the device will be assigned to.

## 4.0 Procedure

1.  **Log In to MySonicwall Portal:**
    -   Navigate to `https://www.mysonicwall.com`.
    -   Log in with your authorized credentials.

2.  **Navigate to Product Registration:**
    -   Once logged in, locate and click on the **Register Products** option in the portal's main navigation menu.

3.  **Select or Create Tenant:**
    -   You will be prompted to associate the device with a tenant.
    -   **If the tenant already exists,** select it from the list.
    -   **If the tenant does not exist,** select the **Create New Tenant** option and follow the on-screen instructions to create it.

4.  **Enter Device Details:**
    -   Enter the **Serial Number** and **Activation Code** from the device or its packaging into the appropriate fields.

5.  **Assign a Friendly Name:**
    -   In the "Friendly Name" field, provide a descriptive name for the device that easily identifies its location or purpose (e.g., `Obera Fairhope`).

6.  **Set Management Options:**
    -   Under the "Management Options" section, select **On Box**.

7.  **Complete Registration:**
    -   Click the **Done** or **Register** button to finalize the process.

## 5.0 Verification

-   After completing the procedure, navigate to the **Products** list within the MySonicwall portal.
-   Confirm that the newly registered device appears in the list, associated with the correct tenant and friendly name.

## 6.0 References

-   MySonicwall Portal: `https://www.mysonicwall.com`

---
**End of Document**
---
```
