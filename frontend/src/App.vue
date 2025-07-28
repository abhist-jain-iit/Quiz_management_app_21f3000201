<template>
  <div id="app">
    <!-- Navigation Bar -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary fixed-top">
      <div class="container">
        <router-link class="navbar-brand" to="/">
          <i class="bi bi-mortarboard-fill me-2"></i>
          Quiz Master V2
        </router-link>

        <button
          class="navbar-toggler"
          type="button"
          data-bs-toggle="collapse"
          data-bs-target="#navbarNav"
        >
          <span class="navbar-toggler-icon"></span>
        </button>

        <div class="collapse navbar-collapse" id="navbarNav">
          <ul class="navbar-nav me-auto">
            <li class="nav-item" v-if="isAuthenticated && !isAdmin">
              <router-link class="nav-link" to="/dashboard">
                <i class="bi bi-speedometer2 me-1"></i>
                Dashboard
              </router-link>
            </li>

            <!-- Admin Navigation - Always visible for admins -->
            <li class="nav-item" v-if="isAdmin">
              <router-link class="nav-link" to="/admin" active-class="active">
                <i class="bi bi-speedometer2 me-1"></i>
                Admin Dashboard
              </router-link>
            </li>
            <li class="nav-item dropdown" v-if="isAdmin">
              <a
                class="nav-link dropdown-toggle"
                href="#"
                role="button"
                data-bs-toggle="dropdown"
                aria-expanded="false"
              >
                <i class="bi bi-gear-fill me-1"></i>
                Admin Panel
              </a>
              <ul class="dropdown-menu">
                <li>
                  <router-link class="dropdown-item" to="/admin/subjects">
                    <i class="bi bi-journal-text me-2"></i>
                    Subjects
                  </router-link>
                </li>
                <li>
                  <router-link class="dropdown-item" to="/admin/chapters">
                    <i class="bi bi-book me-2"></i>
                    Chapters
                  </router-link>
                </li>
                <li>
                  <router-link class="dropdown-item" to="/admin/quizzes">
                    <i class="bi bi-patch-question me-2"></i>
                    Quizzes
                  </router-link>
                </li>
                <li>
                  <router-link class="dropdown-item" to="/admin/questions">
                    <i class="bi bi-question-circle me-2"></i>
                    Questions
                  </router-link>
                </li>
                <li>
                  <router-link class="dropdown-item" to="/admin/users">
                    <i class="bi bi-people me-2"></i>
                    Users
                  </router-link>
                </li>
              </ul>
            </li>
          </ul>

          <ul class="navbar-nav">
            <li class="nav-item dropdown" v-if="isAuthenticated">
              <a
                class="nav-link dropdown-toggle"
                href="#"
                role="button"
                data-bs-toggle="dropdown"
              >
                <i class="bi bi-person-circle me-1"></i>
                {{ user?.full_name || "User" }}
              </a>
              <ul class="dropdown-menu">
                <li>
                  <router-link class="dropdown-item" to="/profile"
                    >Profile</router-link
                  >
                </li>
                <li><hr class="dropdown-divider" /></li>
                <li>
                  <a class="dropdown-item" href="#" @click="logout">Logout</a>
                </li>
              </ul>
            </li>
            <li class="nav-item" v-else>
              <router-link class="nav-link" to="/login">
                <i class="bi bi-box-arrow-in-right me-1"></i>
                Login
              </router-link>
            </li>
          </ul>
        </div>
      </div>
    </nav>

    <!-- Main Content -->
    <main
      class="container-fluid"
      style="margin-top: 80px; min-height: calc(100vh - 80px)"
    >
      <router-view />
    </main>

    <!-- Loading Overlay -->
    <div
      v-if="loading"
      class="position-fixed top-0 start-0 w-100 h-100 d-flex justify-content-center align-items-center"
      style="background-color: rgba(0, 0, 0, 0.7); z-index: 9999"
    >
      <div class="text-center">
        <div
          class="spinner-border text-light mb-3"
          role="status"
          style="width: 3rem; height: 3rem"
        >
          <span class="visually-hidden">Loading...</span>
        </div>
        <div class="text-light h5">Loading Quiz Master V2...</div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted, watch } from "vue";
import { useRouter, useRoute } from "vue-router";

export default {
  name: "App",
  setup() {
    const router = useRouter();
    const route = useRoute();
    const loading = ref(false);
    const user = ref(null);
    const authToken = ref(localStorage.getItem("access_token"));

    // Reactive authentication state
    const isAuthenticated = computed(() => {
      return !!authToken.value && !!user.value;
    });

    const isAdmin = computed(() => {
      return user.value?.is_admin || false;
    });

    const loadUser = () => {
      const userData = localStorage.getItem("user");
      const token = localStorage.getItem("access_token");

      authToken.value = token;

      if (userData && token) {
        try {
          user.value = JSON.parse(userData);
        } catch (e) {
          console.error("Error parsing user data:", e);
          user.value = null;
          authToken.value = null;
          clearAuthData();
        }
      } else {
        user.value = null;
        authToken.value = null;
      }
    };

    const clearAuthData = () => {
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
      localStorage.removeItem("user");
      user.value = null;
      authToken.value = null;
    };

    const logout = async () => {
      try {
        // Optional: Call logout API endpoint
        // await api.logout();
      } catch (error) {
        console.error("Logout API error:", error);
      } finally {
        clearAuthData();
        router.push("/login");
      }
    };

    // Storage event listener for cross-tab synchronization
    const handleStorageChange = (e) => {
      if (e.key === "user" || e.key === "access_token") {
        loadUser();
      }
    };

    // Custom event listener for manual auth updates
    const handleAuthUpdate = () => {
      loadUser();
    };

    onMounted(() => {
      loadUser();
      window.addEventListener("storage", handleStorageChange);
      window.addEventListener("auth-update", handleAuthUpdate);
    });

    onUnmounted(() => {
      window.removeEventListener("storage", handleStorageChange);
      window.removeEventListener("auth-update", handleAuthUpdate);
    });

    // Watch for route changes
    watch(
      () => route.path,
      () => {
        // Force reload user data on route change
        loadUser();
      }
    );

    // Provide global auth update function
    window.updateAuthState = () => {
      loadUser();
      window.dispatchEvent(new CustomEvent("auth-update"));
    };

    return {
      loading,
      user,
      isAuthenticated,
      isAdmin,
      logout,
      loadUser,
    };
  },
};
</script>

<style>
/* Global styles for text visibility across all themes */
:root {
  --text-color: #212529;
  --bg-color: #ffffff;
  --card-bg: #ffffff;
  --border-color: #dee2e6;
  --muted-color: #6c757d;
}

/* Dark theme variables */
@media (prefers-color-scheme: dark) {
  :root {
    --text-color: #ffffff;
    --bg-color: #212529;
    --card-bg: #343a40;
    --border-color: #495057;
    --muted-color: #adb5bd;
  }
}

/* Global text visibility improvements */
body {
  background-color: var(--bg-color);
  color: var(--text-color);
}

.card {
  background-color: var(--card-bg) !important;
  color: var(--text-color) !important;
  border-color: var(--border-color) !important;
}

.card-header {
  background-color: var(--card-bg) !important;
  color: var(--text-color) !important;
  border-bottom-color: var(--border-color) !important;
}

.form-control {
  background-color: var(--bg-color) !important;
  color: var(--text-color) !important;
  border-color: var(--border-color) !important;
}

.form-control:focus {
  background-color: var(--bg-color) !important;
  color: var(--text-color) !important;
}

.form-select {
  background-color: var(--bg-color) !important;
  color: var(--text-color) !important;
  border-color: var(--border-color) !important;
}

.form-select:focus {
  background-color: var(--bg-color) !important;
  color: var(--text-color) !important;
}

.table {
  color: var(--text-color) !important;
  background-color: var(--card-bg) !important;
}

.table th {
  background-color: var(--card-bg) !important;
  color: var(--text-color) !important;
  border-color: var(--border-color) !important;
}

.table td {
  background-color: var(--card-bg) !important;
  color: var(--text-color) !important;
  border-color: var(--border-color) !important;
}

/* Remove striped table styling */
.table-striped > tbody > tr:nth-of-type(odd) > td,
.table-striped > tbody > tr:nth-of-type(odd) > th {
  background-color: var(--card-bg) !important;
}

.table-striped > tbody > tr:nth-of-type(even) > td,
.table-striped > tbody > tr:nth-of-type(even) > th {
  background-color: var(--card-bg) !important;
}

/* Hover effect for table rows */
.table-hover > tbody > tr:hover > td,
.table-hover > tbody > tr:hover > th {
  background-color: var(--bg-color) !important;
  color: var(--text-color) !important;
}

.modal-content {
  background-color: var(--card-bg) !important;
  color: var(--text-color) !important;
}

.modal-header {
  background-color: var(--card-bg) !important;
  color: var(--text-color) !important;
  border-bottom-color: var(--border-color) !important;
}

.modal-footer {
  background-color: var(--card-bg) !important;
  border-top-color: var(--border-color) !important;
}

.text-muted {
  color: var(--muted-color) !important;
}

/* Dropdown menu visibility */
.dropdown-menu {
  background-color: var(--card-bg) !important;
  border-color: var(--border-color) !important;
}

.dropdown-item {
  color: var(--text-color) !important;
}

.dropdown-item:hover {
  background-color: var(--bg-color) !important;
  color: var(--text-color) !important;
}

/* Input group text */
.input-group-text {
  background-color: var(--card-bg) !important;
  color: var(--text-color) !important;
  border-color: var(--border-color) !important;
}

/* Alert components */
.alert {
  color: var(--text-color) !important;
}

/* Badge components */
.badge {
  color: #ffffff !important;
}

/* Ensure buttons maintain their intended colors */
.btn-primary {
  color: #ffffff !important;
}

.btn-secondary {
  color: #ffffff !important;
}

.btn-success {
  color: #ffffff !important;
}

.btn-danger {
  color: #ffffff !important;
}

.btn-warning {
  color: #000000 !important;
}

.btn-info {
  color: #ffffff !important;
}

.btn-light {
  color: #000000 !important;
}

.btn-dark {
  color: #ffffff !important;
}

/* Outline button text visibility */
.btn-outline-primary {
  color: var(--text-color) !important;
}

.btn-outline-secondary {
  color: var(--text-color) !important;
}

.btn-outline-success {
  color: var(--text-color) !important;
}

.btn-outline-danger {
  color: var(--text-color) !important;
}

.btn-outline-warning {
  color: var(--text-color) !important;
}

.btn-outline-info {
  color: var(--text-color) !important;
}

.btn-outline-light {
  color: var(--text-color) !important;
}

.btn-outline-dark {
  color: var(--text-color) !important;
}

/* Navbar specific styling */
.navbar {
  background-color: #0d6efd !important;
}

.navbar-brand {
  color: #ffffff !important;
  font-weight: bold;
}

.navbar-brand:hover {
  color: #ffffff !important;
}

.nav-link {
  color: #ffffff !important;
  font-weight: 500;
}

.nav-link:hover {
  color: #e9ecef !important;
}

.nav-link.active {
  color: #ffffff !important;
  font-weight: bold;
}

.dropdown-toggle {
  color: #ffffff !important;
}

.dropdown-toggle:hover {
  color: #e9ecef !important;
}

.navbar-toggler {
  border-color: #ffffff;
}

.navbar-toggler-icon {
  background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 30 30'%3e%3cpath stroke='rgba%28255, 255, 255, 0.75%29' stroke-linecap='round' stroke-miterlimit='10' stroke-width='2' d='M4 7h22M4 15h22M4 23h22'/%3e%3c/svg%3e");
}

/* Breadcrumb and Navigation Styling */
.breadcrumb {
  background-color: var(--card-bg) !important;
  border-radius: 0.375rem;
  padding: 0.75rem 1rem;
  margin-bottom: 1rem;
}

.breadcrumb-item {
  color: var(--text-color) !important;
}

.breadcrumb-item.active {
  color: var(--muted-color) !important;
}

.breadcrumb-item + .breadcrumb-item::before {
  color: var(--muted-color) !important;
}

.breadcrumb a {
  color: var(--bs-primary) !important;
  text-decoration: none;
}

.breadcrumb a:hover {
  color: var(--bs-primary) !important;
  text-decoration: underline;
}

/* Admin dropdown menu styling */
.dropdown-menu {
  border: 1px solid var(--border-color) !important;
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15) !important;
}

.dropdown-item {
  padding: 0.5rem 1rem !important;
  transition: all 0.2s ease-in-out;
}

.dropdown-item:hover {
  background-color: var(--bs-primary) !important;
  color: #ffffff !important;
}

.dropdown-item i {
  width: 1.2rem;
  text-align: center;
}

/* Back button styling */
.btn-outline-secondary {
  border-color: var(--border-color) !important;
  color: var(--text-color) !important;
}

.btn-outline-secondary:hover {
  background-color: var(--bs-secondary) !important;
  border-color: var(--bs-secondary) !important;
  color: #ffffff !important;
}
</style>
