<template>
  <div class="container-fluid">
    <div class="row">
      <div class="col-12">
        <div class="d-flex justify-content-between align-items-center mb-4">
          <h2 class="mb-0">
            <i class="bi bi-people me-2"></i>
            User Management
          </h2>
        </div>

        <!-- Search and Filter -->
        <div class="card mb-4">
          <div class="card-body">
            <div class="row g-3">
              <div class="col-md-4">
                <input
                  type="text"
                  class="form-control"
                  placeholder="Search users..."
                  v-model="searchQuery"
                  @input="loadUsers"
                />
              </div>
              <div class="col-md-3">
                <select
                  class="form-select"
                  v-model="roleFilter"
                  @change="loadUsers"
                >
                  <option value="">All Roles</option>
                  <option value="admin">Admin</option>
                  <option value="user">User</option>
                </select>
              </div>
              <div class="col-md-2">
                <button class="btn btn-outline-primary" @click="loadUsers">
                  <i class="bi bi-search me-2"></i>
                  Search
                </button>
              </div>
              <div class="col-md-3">
                <button class="btn btn-outline-secondary" @click="resetFilters">
                  <i class="bi bi-arrow-clockwise me-2"></i>
                  Reset
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Users Table -->
        <div class="card">
          <div class="card-header">
            <h5 class="mb-0">Users ({{ users.length }})</h5>
          </div>
          <div class="card-body">
            <div v-if="loading" class="text-center py-4">
              <div class="spinner-border" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>

            <div
              v-else-if="users.length === 0"
              class="text-center py-4 text-muted"
            >
              <i class="bi bi-person-x fs-1 mb-3"></i>
              <p>No users found</p>
            </div>

            <div v-else class="table-responsive">
              <table class="table table-striped table-hover">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>Email</th>
                    <th>Username</th>
                    <th>Role</th>
                    <th>Status</th>
                    <th>Joined</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="user in users" :key="user.id">
                    <td>{{ user.id }}</td>
                    <td>
                      <div class="d-flex align-items-center">
                        <div
                          class="bg-primary text-white rounded-circle d-flex align-items-center justify-content-center me-2"
                          style="width: 32px; height: 32px; font-size: 0.8rem"
                        >
                          {{ user.full_name.charAt(0).toUpperCase() }}
                        </div>
                        <div>
                          <strong>{{ user.full_name }}</strong>
                          <br />
                          <small class="text-muted" v-if="user.qualification">{{
                            user.qualification
                          }}</small>
                        </div>
                      </div>
                    </td>
                    <td>{{ user.email }}</td>
                    <td>{{ user.username }}</td>
                    <td>
                      <span
                        class="badge"
                        :class="user.is_admin ? 'bg-danger' : 'bg-primary'"
                      >
                        {{ user.is_admin ? "Admin" : "User" }}
                      </span>
                    </td>
                    <td>
                      <span
                        class="badge"
                        :class="user.is_active ? 'bg-success' : 'bg-secondary'"
                      >
                        {{ user.is_active ? "Active" : "Inactive" }}
                      </span>
                    </td>
                    <td>{{ formatDate(user.created_at) }}</td>
                    <td>
                      <div class="btn-group btn-group-sm">
                        <button
                          class="btn btn-outline-primary"
                          @click="viewUser(user)"
                        >
                          <i class="bi bi-eye"></i>
                        </button>
                        <button
                          class="btn btn-outline-warning"
                          @click="editUser(user)"
                          v-if="!user.is_admin"
                        >
                          <i class="bi bi-pencil"></i>
                        </button>
                        <button
                          class="btn btn-outline-danger"
                          @click="confirmDelete(user)"
                          v-if="!user.is_admin"
                        >
                          <i class="bi bi-trash"></i>
                        </button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- View User Modal -->
    <div
      class="modal fade"
      :class="{ show: showViewModal }"
      :style="{ display: showViewModal ? 'block' : 'none' }"
      tabindex="-1"
    >
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">User Details</h5>
            <button
              type="button"
              class="btn-close"
              @click="showViewModal = false"
            ></button>
          </div>
          <div class="modal-body" v-if="selectedUser">
            <div class="row">
              <div class="col-md-4 text-center mb-4">
                <div
                  class="bg-primary text-white rounded-circle d-inline-flex align-items-center justify-content-center mb-3"
                  style="width: 80px; height: 80px; font-size: 2rem"
                >
                  {{ selectedUser.full_name.charAt(0).toUpperCase() }}
                </div>
                <h5>{{ selectedUser.full_name }}</h5>
                <p class="text-muted">{{ selectedUser.email }}</p>
              </div>

              <div class="col-md-8">
                <table class="table table-borderless">
                  <tbody>
                    <tr>
                      <td><strong>Username:</strong></td>
                      <td>{{ selectedUser.username }}</td>
                    </tr>
                    <tr>
                      <td><strong>Role:</strong></td>
                      <td>
                        <span
                          class="badge"
                          :class="
                            selectedUser.is_admin ? 'bg-danger' : 'bg-primary'
                          "
                        >
                          {{ selectedUser.is_admin ? "Admin" : "User" }}
                        </span>
                      </td>
                    </tr>
                    <tr>
                      <td><strong>Status:</strong></td>
                      <td>
                        <span
                          class="badge"
                          :class="
                            selectedUser.is_active
                              ? 'bg-success'
                              : 'bg-secondary'
                          "
                        >
                          {{ selectedUser.is_active ? "Active" : "Inactive" }}
                        </span>
                      </td>
                    </tr>
                    <tr v-if="selectedUser.qualification">
                      <td><strong>Qualification:</strong></td>
                      <td>{{ selectedUser.qualification }}</td>
                    </tr>
                    <tr v-if="selectedUser.date_of_birth">
                      <td><strong>Date of Birth:</strong></td>
                      <td>{{ formatDate(selectedUser.date_of_birth) }}</td>
                    </tr>
                    <tr>
                      <td><strong>Member Since:</strong></td>
                      <td>{{ formatDate(selectedUser.created_at) }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div
      v-if="showViewModal"
      class="modal-backdrop fade show"
      @click="showViewModal = false"
    ></div>

    <!-- Edit User Modal -->
    <div
      class="modal fade"
      :class="{ show: showEditModal }"
      :style="{ display: showEditModal ? 'block' : 'none' }"
      tabindex="-1"
    >
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Edit User</h5>
            <button
              type="button"
              class="btn-close"
              @click="closeEditModal"
            ></button>
          </div>
          <form @submit.prevent="saveUser">
            <div class="modal-body">
              <div class="mb-3">
                <label for="fullName" class="form-label">Full Name *</label>
                <input
                  type="text"
                  class="form-control"
                  id="fullName"
                  v-model="userForm.full_name"
                  required
                />
              </div>

              <div class="mb-3">
                <label for="qualification" class="form-label"
                  >Qualification</label
                >
                <input
                  type="text"
                  class="form-control"
                  id="qualification"
                  v-model="userForm.qualification"
                />
              </div>

              <div class="mb-3">
                <label for="dateOfBirth" class="form-label"
                  >Date of Birth</label
                >
                <input
                  type="date"
                  class="form-control"
                  id="dateOfBirth"
                  v-model="userForm.date_of_birth"
                />
              </div>

              <div class="mb-3">
                <div class="form-check">
                  <input
                    class="form-check-input"
                    type="checkbox"
                    id="isActive"
                    v-model="userForm.is_active"
                  />
                  <label class="form-check-label" for="isActive">
                    Active User
                  </label>
                </div>
              </div>

              <div class="alert alert-danger" v-if="errorMessage">
                <i class="bi bi-exclamation-triangle me-2"></i>
                {{ errorMessage }}
              </div>
            </div>
            <div class="modal-footer">
              <button
                type="button"
                class="btn btn-secondary"
                @click="closeEditModal"
              >
                Cancel
              </button>
              <button type="submit" class="btn btn-primary" :disabled="saving">
                <span
                  v-if="saving"
                  class="spinner-border spinner-border-sm me-2"
                ></span>
                Update User
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
    <div
      v-if="showEditModal"
      class="modal-backdrop fade show"
      @click="closeEditModal"
    ></div>

    <!-- Delete Confirmation Modal -->
    <div
      class="modal fade"
      :class="{ show: showDeleteModal }"
      :style="{ display: showDeleteModal ? 'block' : 'none' }"
      tabindex="-1"
    >
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Delete User</h5>
            <button
              type="button"
              class="btn-close"
              @click="showDeleteModal = false"
            ></button>
          </div>
          <div class="modal-body">
            <p>
              Are you sure you want to delete the user
              <strong>{{ userToDelete?.full_name }}</strong
              >?
            </p>
            <p class="text-warning">
              This action cannot be undone and will also delete all associated
              quiz attempts.
            </p>
          </div>
          <div class="modal-footer">
            <button
              type="button"
              class="btn btn-secondary"
              @click="showDeleteModal = false"
            >
              Cancel
            </button>
            <button
              type="button"
              class="btn btn-danger"
              @click="deleteUser"
              :disabled="deleting"
            >
              <span
                v-if="deleting"
                class="spinner-border spinner-border-sm me-2"
              ></span>
              Delete
            </button>
          </div>
        </div>
      </div>
    </div>
    <div
      v-if="showDeleteModal"
      class="modal-backdrop fade show"
      @click="showDeleteModal = false"
    ></div>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from "vue";
import api from "../../services/api";

export default {
  name: "UserManagement",
  setup() {
    const loading = ref(false);
    const saving = ref(false);
    const deleting = ref(false);
    const users = ref([]);
    const searchQuery = ref("");
    const roleFilter = ref("");
    const showViewModal = ref(false);
    const showEditModal = ref(false);
    const showDeleteModal = ref(false);
    const selectedUser = ref(null);
    const editingUser = ref(null);
    const userToDelete = ref(null);
    const errorMessage = ref("");

    const userForm = reactive({
      full_name: "",
      qualification: "",
      date_of_birth: "",
      is_active: true,
    });

    const loadUsers = async () => {
      loading.value = true;
      try {
        const params = {};
        if (searchQuery.value.trim()) {
          params.search = searchQuery.value.trim();
        }
        if (roleFilter.value) {
          params.role = roleFilter.value;
        }

        const response = await api.getUsers(params);
        users.value = response;
      } catch (error) {
        console.error("Error loading users:", error);
      } finally {
        loading.value = false;
      }
    };

    const resetFilters = () => {
      searchQuery.value = "";
      roleFilter.value = "";
      loadUsers();
    };

    const viewUser = (user) => {
      selectedUser.value = user;
      showViewModal.value = true;
    };

    const editUser = (user) => {
      editingUser.value = user;
      userForm.full_name = user.full_name;
      userForm.qualification = user.qualification || "";
      userForm.date_of_birth = user.date_of_birth || "";
      userForm.is_active = user.is_active;
      showEditModal.value = true;
    };

    const saveUser = async () => {
      saving.value = true;
      errorMessage.value = "";

      try {
        const data = {
          full_name: userForm.full_name.trim(),
          qualification: userForm.qualification.trim(),
          date_of_birth: userForm.date_of_birth,
          is_active: userForm.is_active,
        };

        await api.updateUser(editingUser.value.id, data);
        closeEditModal();
        loadUsers();
      } catch (error) {
        console.error("Error updating user:", error);
        errorMessage.value =
          error.response?.data?.message || "Failed to update user";
      } finally {
        saving.value = false;
      }
    };

    const confirmDelete = (user) => {
      userToDelete.value = user;
      showDeleteModal.value = true;
    };

    const deleteUser = async () => {
      deleting.value = true;

      try {
        await api.deleteUser(userToDelete.value.id);
        showDeleteModal.value = false;
        loadUsers();
      } catch (error) {
        console.error("Error deleting user:", error);
        alert("Failed to delete user.");
      } finally {
        deleting.value = false;
      }
    };

    const closeEditModal = () => {
      showEditModal.value = false;
      editingUser.value = null;
      userForm.full_name = "";
      userForm.qualification = "";
      userForm.date_of_birth = "";
      userForm.is_active = true;
      errorMessage.value = "";
    };

    const formatDate = (dateString) => {
      if (!dateString) return "";
      return new Date(dateString).toLocaleDateString();
    };

    onMounted(() => {
      loadUsers();
    });

    return {
      loading,
      saving,
      deleting,
      users,
      searchQuery,
      roleFilter,
      showViewModal,
      showEditModal,
      showDeleteModal,
      selectedUser,
      editingUser,
      userToDelete,
      userForm,
      errorMessage,
      loadUsers,
      resetFilters,
      viewUser,
      editUser,
      saveUser,
      confirmDelete,
      deleteUser,
      closeEditModal,
      formatDate,
    };
  },
};
</script>
