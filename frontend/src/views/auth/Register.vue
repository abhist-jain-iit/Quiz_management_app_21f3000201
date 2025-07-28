<template>
  <div class="container">
    <div class="row justify-content-center">
      <div class="col-md-8 col-lg-6">
        <div class="card shadow">
          <div class="card-body p-4">
            <div class="text-center mb-4">
              <i class="bi bi-person-plus text-primary fs-1"></i>
              <h3 class="mt-2">Register for Quiz Master</h3>
              <p class="text-muted">Create your account to start learning</p>
            </div>

            <form @submit.prevent="handleRegister">
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label for="username" class="form-label">Username *</label>
                  <input
                    type="text"
                    class="form-control"
                    id="username"
                    v-model="form.username"
                    :class="{ 'is-invalid': errors.username }"
                    required
                  />
                  <div class="invalid-feedback" v-if="errors.username">
                    {{ errors.username }}
                  </div>
                </div>

                <div class="col-md-6 mb-3">
                  <label for="email" class="form-label">Email *</label>
                  <input
                    type="email"
                    class="form-control"
                    id="email"
                    v-model="form.email"
                    :class="{ 'is-invalid': errors.email }"
                    required
                  />
                  <div class="invalid-feedback" v-if="errors.email">
                    {{ errors.email }}
                  </div>
                </div>
              </div>

              <div class="mb-3">
                <label for="full_name" class="form-label">Full Name *</label>
                <input
                  type="text"
                  class="form-control"
                  id="full_name"
                  v-model="form.full_name"
                  :class="{ 'is-invalid': errors.full_name }"
                  required
                />
                <div class="invalid-feedback" v-if="errors.full_name">
                  {{ errors.full_name }}
                </div>
              </div>

              <div class="row">
                <div class="col-md-6 mb-3">
                  <label for="qualification" class="form-label"
                    >Qualification</label
                  >
                  <input
                    type="text"
                    class="form-control"
                    id="qualification"
                    v-model="form.qualification"
                    placeholder="e.g., B.Tech, M.Sc, etc."
                  />
                </div>

                <div class="col-md-6 mb-3">
                  <label for="date_of_birth" class="form-label"
                    >Date of Birth</label
                  >
                  <input
                    type="date"
                    class="form-control"
                    id="date_of_birth"
                    v-model="form.date_of_birth"
                    :class="{ 'is-invalid': errors.date_of_birth }"
                  />
                  <div class="invalid-feedback" v-if="errors.date_of_birth">
                    {{ errors.date_of_birth }}
                  </div>
                </div>
              </div>

              <div class="mb-3">
                <label for="password" class="form-label">Password *</label>
                <div class="input-group">
                  <input
                    :type="showPassword ? 'text' : 'password'"
                    class="form-control"
                    id="password"
                    v-model="form.password"
                    :class="{ 'is-invalid': errors.password }"
                    required
                  />
                  <button
                    type="button"
                    class="btn btn-outline-secondary"
                    @click="showPassword = !showPassword"
                  >
                    <i
                      :class="showPassword ? 'bi bi-eye-slash' : 'bi bi-eye'"
                    ></i>
                  </button>
                </div>
                <div class="invalid-feedback" v-if="errors.password">
                  {{ errors.password }}
                </div>
                <div class="form-text">
                  Password must be at least 8 characters long
                </div>
              </div>

              <div class="mb-3">
                <label for="confirmPassword" class="form-label"
                  >Confirm Password *</label
                >
                <input
                  type="password"
                  class="form-control"
                  id="confirmPassword"
                  v-model="form.confirmPassword"
                  :class="{ 'is-invalid': errors.confirmPassword }"
                  required
                />
                <div class="invalid-feedback" v-if="errors.confirmPassword">
                  {{ errors.confirmPassword }}
                </div>
              </div>

              <div class="alert alert-danger" v-if="errorMessage">
                <i class="bi bi-exclamation-triangle me-2"></i>
                {{ errorMessage }}
              </div>

              <div class="d-grid mb-3">
                <button
                  type="submit"
                  class="btn btn-primary"
                  :disabled="loading"
                >
                  <span
                    v-if="loading"
                    class="spinner-border spinner-border-sm me-2"
                  ></span>
                  <i v-else class="bi bi-person-plus me-2"></i>
                  {{ loading ? "Creating Account..." : "Register" }}
                </button>
              </div>
            </form>

            <div class="text-center">
              <p class="mb-0">
                Already have an account?
                <router-link to="/login" class="text-decoration-none">
                  Login here
                </router-link>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive } from "vue";
import { useRouter } from "vue-router";
import api from "../../services/api";

export default {
  name: "Register",
  setup() {
    const router = useRouter();
    const loading = ref(false);
    const showPassword = ref(false);
    const errorMessage = ref("");

    const form = reactive({
      username: "",
      email: "",
      full_name: "",
      qualification: "",
      date_of_birth: "",
      password: "",
      confirmPassword: "",
    });

    const errors = reactive({
      username: "",
      email: "",
      full_name: "",
      date_of_birth: "",
      password: "",
      confirmPassword: "",
    });

    const validateForm = () => {
      // Reset errors
      Object.keys(errors).forEach((key) => (errors[key] = ""));

      let isValid = true;

      if (!form.username.trim()) {
        errors.username = "Username is required";
        isValid = false;
      } else if (form.username.length < 3) {
        errors.username = "Username must be at least 3 characters";
        isValid = false;
      }

      if (!form.email.trim()) {
        errors.email = "Email is required";
        isValid = false;
      } else if (!/\S+@\S+\.\S+/.test(form.email)) {
        errors.email = "Please enter a valid email";
        isValid = false;
      }

      if (!form.full_name.trim()) {
        errors.full_name = "Full name is required";
        isValid = false;
      }

      if (!form.password) {
        errors.password = "Password is required";
        isValid = false;
      } else if (form.password.length < 8) {
        errors.password = "Password must be at least 8 characters";
        isValid = false;
      }

      if (!form.confirmPassword) {
        errors.confirmPassword = "Please confirm your password";
        isValid = false;
      } else if (form.password !== form.confirmPassword) {
        errors.confirmPassword = "Passwords do not match";
        isValid = false;
      }

      return isValid;
    };

    const handleRegister = async () => {
      if (!validateForm()) return;

      loading.value = true;
      errorMessage.value = "";

      try {
        const registerData = {
          username: form.username.trim(),
          email: form.email.trim(),
          full_name: form.full_name.trim(),
          password: form.password,
        };

        if (form.qualification.trim()) {
          registerData.qualification = form.qualification.trim();
        }

        if (form.date_of_birth) {
          registerData.date_of_birth = form.date_of_birth;
        }

        const response = await api.register(registerData);

        // Store tokens and user data
        localStorage.setItem("access_token", response.access_token);
        localStorage.setItem("refresh_token", response.refresh_token);
        localStorage.setItem("user", JSON.stringify(response.user));

        // Redirect to dashboard
        router.push("/dashboard");
      } catch (error) {
        console.error("Registration error:", error);
        errorMessage.value =
          error.response?.data?.message ||
          "Registration failed. Please try again.";
      } finally {
        loading.value = false;
      }
    };

    return {
      form,
      errors,
      loading,
      showPassword,
      errorMessage,
      handleRegister,
    };
  },
};
</script>
