        function showUserInfo() {
            const headerRight = document.querySelector('.header-right');
            if (headerRight) {
                const userInfoHtml = `
                    <div class="user-info" id="userInfoDisplay">
                        <div class="user-avatar">${getInitials(currentUser.displayName)}</div>
