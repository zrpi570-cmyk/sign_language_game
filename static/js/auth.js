var Auth = (function() {
    var BASE = "";
    var currentUser = null;
    var _readyResolve = null;
    var _readyPromise = new Promise(function(resolve) { _readyResolve = resolve; });
    var _initialized = false;

    function getUser() { return currentUser; }
    function isLoggedIn() { return currentUser !== null; }
    function ready() { return _readyPromise; }
    function isInitialized() { return _initialized; }

    async function init() {
        try {
            var res = await fetch(BASE + "/api/auth/me");
            var data = await res.json();
            if (data.code === 0) {
                setUser(data.data);
                _initialized = true;
                _readyResolve();
                return true;
            }
        } catch(e) {}
        showGuestUI();
        _initialized = true;
        _readyResolve();
        return false;
    }

    function setUser(user) {
        currentUser = user;
        // 更新传统导航栏（旧页面）
        var authSection = document.getElementById("authSection");
        var userSection = document.getElementById("userSection");
        if (authSection) authSection.style.display = "none";
        if (userSection) {
            userSection.style.display = "flex";
            var badge = document.getElementById("userBadge");
            if (badge) badge.textContent = user.username + " Lv." + (user.level || 1);
        }
        // 触发登录事件（供所有页面监听）
        document.dispatchEvent(new CustomEvent("auth:login", { detail: user }));
    }

    function showGuestUI() {
        currentUser = null;
        var authSection = document.getElementById("authSection");
        var userSection = document.getElementById("userSection");
        if (authSection) authSection.style.display = "flex";
        if (userSection) userSection.style.display = "none";
        document.dispatchEvent(new CustomEvent("auth:logout"));
    }

    async function login(username, password) {
        if (!username) return { error: "请输入用户名" };
        try {
            var res = await fetch(BASE + "/api/auth/login", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({username: username, password: password || ""})
            });
            var data = await res.json();
            if (data.code === 0) {
                setUser(data.data);
                return { ok: true, user: data.data };
            }
            if (!password) {
                var r2 = await fetch(BASE + "/api/auth/guest", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({username: username})
                });
                var d2 = await r2.json();
                if (d2.code === 0) {
                    setUser(d2.data);
                    return { ok: true, user: d2.data };
                }
            }
            return { error: data.message };
        } catch(e) {
            return { error: "网络错误: " + e.message };
        }
    }

    async function register(username, password, confirm) {
        if (!username) return { error: "请输入用户名" };
        if (!password || password.length < 4) return { error: "密码至少4位" };
        if (password !== confirm) return { error: "两次密码不一致" };
        try {
            var res = await fetch(BASE + "/api/auth/register", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({username: username, password: password})
            });
            var data = await res.json();
            if (data.code === 0) {
                setUser(data.data);
                return { ok: true, user: data.data };
            }
            return { error: data.message };
        } catch(e) {
            return { error: "网络错误: " + e.message };
        }
    }

    async function logout() {
        await fetch(BASE + "/api/auth/logout", { method: "POST" });
        showGuestUI();
    }

    function showAuthModal(mode) {
        var modal = document.getElementById("authModal");
        if (!modal) {
            modal = document.createElement("div");
            modal.id = "authModal";
            modal.className = "modal";
            modal.style.display = "none";
            modal.innerHTML =
                '<div class="modal-backdrop" onclick="Auth.hideAuthModal()"></div>' +
                '<div class="modal-content" style="max-width:400px">' +
                '<div class="modal-close" onclick="Auth.hideAuthModal()">&times;</div>' +
                '<div style="padding:32px">' +
                '<h2 style="margin-bottom:20px" id="authModalTitle">登录</h2>' +
                '<div class="form-group"><label>用户名</label>' +
                '<input type="text" id="authModalUsername" class="form-input" maxlength="20" placeholder="给自己起个名字"></div>' +
                '<div class="form-group"><label>密码</label>' +
                '<input type="password" id="authModalPassword" class="form-input" placeholder="密码"></div>' +
                '<div class="form-group" id="authModalConfirmGroup"><label>确认密码</label>' +
                '<input type="password" id="authModalConfirm" class="form-input" placeholder="再次输入密码"></div>' +
                '<div id="authModalError" class="form-error" style="display:none"></div>' +
                '<div style="display:flex;gap:10px;margin-top:16px">' +
                '<button id="authModalSubmitBtn" class="btn btn-primary" style="flex:1">登录</button>' +
                '<button id="authModalToggleBtn" class="btn btn-secondary">注册新账号</button></div></div></div>';
            document.body.appendChild(modal);
            document.getElementById("authModalSubmitBtn").addEventListener("click", handleModalSubmit);
            document.getElementById("authModalToggleBtn").addEventListener("click", toggleModalMode);
            document.getElementById("authModalPassword").addEventListener("keydown", function(e) {
                if (e.key === "Enter") handleModalSubmit();
            });
        }
        modal._mode = mode || "login";
        updateModalUI(modal._mode);
        modal.style.display = "flex";
        document.getElementById("authModalError").style.display = "none";
        document.getElementById("authModalUsername").value = "";
        document.getElementById("authModalPassword").value = "";
        document.getElementById("authModalConfirm").value = "";
        setTimeout(function() { document.getElementById("authModalUsername").focus(); }, 100);
    }

    function hideAuthModal() {
        var modal = document.getElementById("authModal");
        if (modal) modal.style.display = "none";
    }

    function updateModalUI(mode) {
        var isReg = mode === "register";
        document.getElementById("authModalTitle").textContent = isReg ? "注册账号" : "登录";
        document.getElementById("authModalSubmitBtn").textContent = isReg ? "注册" : "登录";
        document.getElementById("authModalToggleBtn").textContent = isReg ? "已有账号？去登录" : "没有账号？去注册";
        document.getElementById("authModalConfirmGroup").style.display = isReg ? "block" : "none";
    }

    function toggleModalMode() {
        var modal = document.getElementById("authModal");
        if (!modal) return;
        var newMode = modal._mode === "login" ? "register" : "login";
        modal._mode = newMode;
        updateModalUI(newMode);
        document.getElementById("authModalError").style.display = "none";
    }

    async function handleModalSubmit() {
        var modal = document.getElementById("authModal");
        if (!modal) return;
        var username = document.getElementById("authModalUsername").value.trim();
        var password = document.getElementById("authModalPassword").value;
        var errDiv = document.getElementById("authModalError");
        var result;
        if (modal._mode === "register") {
            var confirm = document.getElementById("authModalConfirm").value;
            result = await register(username, password, confirm);
        } else {
            result = await login(username, password);
        }
        if (result.error) {
            errDiv.textContent = result.error;
            errDiv.style.display = "block";
            return;
        }
        hideAuthModal();
    }

    return {
        init: init,
        ready: ready,
        getUser: getUser,
        isLoggedIn: isLoggedIn,
        isInitialized: isInitialized,
        login: login,
        register: register,
        logout: logout,
        showAuthModal: showAuthModal,
        hideAuthModal: hideAuthModal,
        setUser: setUser
    };
})();

document.addEventListener("DOMContentLoaded", function() { Auth.init(); });
