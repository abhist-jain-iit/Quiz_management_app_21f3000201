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
            <li class="nav-item" v-if="isAuthenticated">
              <router-link class="nav-link" to="/dashboard">
                <i class="bi bi-speedometer2 me-1"></i>
                Dashboard
              </router-link>
            </li>
            <li class="nav-item" v-if="isAdmin">
              <router-link class="nav-link" to="/admin">
                <i class="bi bi-gear-fill me-1"></i>
                Admin Panel
              </router-link>
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
      style="background-color: rgba(0, 0, 0, 0.5); z-index: 9999"
    >
      <div class="spinner-border text-light" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from "vue";
import { useRouter } from "vue-router";

export default {
  name: "App",
  setup() {
    const router = useRouter();
    const loading = ref(false);
    const user = ref(null);

    const isAuthenticated = computed(() => {
      return !!localStorage.getItem("access_token") && !!user.value;
    });

    const isAdmin = computed(() => {
      return user.value?.is_admin || false;
    });

    const loadUser = () => {
      const userData = localStorage.getItem("user");
      if (userData) {
        user.value = JSON.parse(userData);
      }
    };

    const logout = () => {
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
      localStorage.removeItem("user");
      user.value = null;
      router.push("/login");
    };

    onMounted(() => {
      loadUser();
    });

    return {
      loading,
      user,
      isAuthenticated,
      isAdmin,
      logout,
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
}

.table th {
  background-color: var(--card-bg) !important;
  color: var(--text-color) !important;
  border-color: var(--border-color) !important;
}

.table td {
  border-color: var(--border-color) !important;
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
</style>
