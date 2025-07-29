<template>
  <div id="app">
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary fixed-top">
      <div class="container">
        <router-link class="navbar-brand" to="/">Quiz Master V2</router-link>

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
              <router-link class="nav-link" to="/dashboard"
                >Dashboard</router-link
              >
            </li>
            <li class="nav-item" v-if="isAdmin">
              <router-link class="nav-link" to="/admin"
                >Admin Dashboard</router-link
              >
            </li>
            <li class="nav-item dropdown" v-if="isAdmin">
              <a
                class="nav-link dropdown-toggle"
                href="#"
                role="button"
                data-bs-toggle="dropdown"
              >
                Admin Panel
              </a>
              <ul class="dropdown-menu">
                <li>
                  <router-link class="dropdown-item" to="/admin/subjects"
                    >Subjects</router-link
                  >
                </li>
                <li>
                  <router-link class="dropdown-item" to="/admin/chapters"
                    >Chapters</router-link
                  >
                </li>
                <li>
                  <router-link class="dropdown-item" to="/admin/quizzes"
                    >Quizzes</router-link
                  >
                </li>
                <li>
                  <router-link class="dropdown-item" to="/admin/questions"
                    >Questions</router-link
                  >
                </li>
                <li>
                  <router-link class="dropdown-item" to="/admin/users"
                    >Users</router-link
                  >
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
              <router-link class="nav-link" to="/login">Login</router-link>
            </li>
          </ul>
        </div>
      </div>
    </nav>

    <main
      class="container-fluid"
      style="margin-top: 80px; min-height: calc(100vh - 80px)"
    >
      <router-view />
    </main>

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
        <div class="text-light h5">Loading...</div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from "vue";
import { useRouter } from "vue-router";

export default {
  name: "App",
  setup() {
    const router = useRouter();
    const loading = ref(false);
    const user = ref(null);
    const authToken = ref(localStorage.getItem("access_token"));

    const isAuthenticated = computed(() => !!authToken.value && !!user.value);
    const isAdmin = computed(() => user.value?.is_admin || false);

    const loadUser = () => {
      const userData = localStorage.getItem("user");
      const token = localStorage.getItem("access_token");
      authToken.value = token;

      if (userData && token) {
        try {
          user.value = JSON.parse(userData);
        } catch (e) {
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

    const logout = () => {
      clearAuthData();
      router.push("/login");
    };

    const handleStorageChange = (e) => {
      if (e.key === "user" || e.key === "access_token") {
        loadUser();
      }
    };

    onMounted(() => {
      loadUser();
      window.addEventListener("storage", handleStorageChange);
    });

    onUnmounted(() => {
      window.removeEventListener("storage", handleStorageChange);
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
body {
  background-color: #f8f9fa;
  color: #212529;
}

.card {
  background-color: #ffffff;
  color: #212529;
  border: 1px solid #dee2e6;
}

.card-header {
  background-color: #f8f9fa;
  color: #212529;
  border-bottom: 1px solid #dee2e6;
}

.form-control,
.form-select {
  background-color: #ffffff;
  color: #212529;
  border: 1px solid #ced4da;
}

.table {
  color: #212529;
  background-color: #ffffff;
}

.table th,
.table td {
  background-color: #ffffff;
  color: #212529;
  border-color: #dee2e6;
}

.modal-content {
  background-color: #ffffff;
  color: #212529;
}

.dropdown-menu {
  background-color: #ffffff;
  border: 1px solid #dee2e6;
}

.dropdown-item {
  color: #212529;
}

.dropdown-item:hover {
  background-color: #0d6efd;
  color: #ffffff;
}

.navbar {
  background-color: #0d6efd !important;
}

.navbar-brand,
.nav-link {
  color: #ffffff !important;
}

.navbar-brand:hover,
.nav-link:hover {
  color: #e9ecef !important;
}
</style>
