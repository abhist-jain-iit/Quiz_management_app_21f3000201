<template>
  <div class="container-fluid">
    <div class="row">
      <div class="col-12">
        <!-- Back Navigation -->
        <nav aria-label="breadcrumb" class="mb-3">
          <ol class="breadcrumb">
            <li class="breadcrumb-item">
              <router-link to="/admin" class="text-decoration-none">
                <i class="bi bi-house me-1"></i>
                Admin Dashboard
              </router-link>
            </li>
            <li class="breadcrumb-item active" aria-current="page">
              <i class="bi bi-journal-text me-1"></i>
              Subject Management
            </li>
          </ol>
        </nav>

        <div class="d-flex justify-content-between align-items-center mb-4">
          <div class="d-flex align-items-center">
            <router-link to="/admin" class="btn btn-outline-secondary me-3">
              <i class="bi bi-arrow-left me-2"></i>
              Back to Dashboard
            </router-link>
            <h2 class="mb-0">
              <i class="bi bi-journal-text me-2"></i>
              Subject Management
            </h2>
          </div>
          <button class="btn btn-primary" @click="showCreateModal = true">
            <i class="bi bi-plus-circle me-2"></i>
            Add Subject
          </button>
        </div>

        <!-- Search and Filter -->
        <div class="card mb-4">
          <div class="card-body">
            <div class="row g-3">
              <div class="col-md-6">
                <input
                  type="text"
                  class="form-control"
                  placeholder="Search subjects..."
                  v-model="searchQuery"
                  @input="loadSubjects"
                />
              </div>
              <div class="col-md-3">
                <button class="btn btn-outline-primary" @click="loadSubjects">
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

        <!-- Subjects Table -->
        <div class="card">
          <div class="card-header">
            <h5 class="mb-0">Subjects ({{ subjects.length }})</h5>
          </div>
          <div class="card-body">
            <div v-if="loading" class="text-center py-4">
              <div class="spinner-border" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>

            <div
              v-else-if="subjects.length === 0"
              class="text-center py-4 text-muted"
            >
              <i class="bi bi-journal-x fs-1 mb-3"></i>
              <p>No subjects found</p>
            </div>

            <div v-else class="table-responsive">
              <table class="table table-striped table-hover">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>Description</th>
                    <th>Chapters</th>
                    <th>Created</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="subject in subjects" :key="subject.id">
                    <td>{{ subject.id }}</td>
                    <td>
                      <strong>{{ subject.name }}</strong>
                    </td>
                    <td>
                      <span v-if="subject.description"
                        >{{ subject.description.substring(0, 100)
                        }}{{
                          subject.description.length > 100 ? "..." : ""
                        }}</span
                      >
                      <span v-else class="text-muted">No description</span>
                    </td>
                    <td>
                      <span class="badge bg-info"
                        >{{ subject.chapter_count || 0 }} chapters</span
                      >
                    </td>
                    <td>{{ formatDate(subject.created_at) }}</td>
                    <td>
                      <div class="btn-group btn-group-sm">
                        <button
                          class="btn btn-outline-primary"
                          @click="editSubject(subject)"
                        >
                          <i class="bi bi-pencil"></i>
                        </button>
                        <button
                          class="btn btn-outline-danger"
                          @click="confirmDelete(subject)"
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

    <!-- Create/Edit Subject Modal -->
    <div
      class="modal fade"
      :class="{ show: showCreateModal || showEditModal }"
      :style="{ display: showCreateModal || showEditModal ? 'block' : 'none' }"
      tabindex="-1"
    >
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">
              {{ editingSubject ? "Edit Subject" : "Create Subject" }}
            </h5>
            <button
              type="button"
              class="btn-close"
              @click="closeModal"
            ></button>
          </div>
          <form @submit.prevent="saveSubject">
            <div class="modal-body">
              <div class="mb-3">
                <label for="subjectName" class="form-label"
                  >Subject Name *</label
                >
                <input
                  type="text"
                  class="form-control"
                  id="subjectName"
                  v-model="subjectForm.name"
                  :class="{ 'is-invalid': errors.name }"
                  required
                />
                <div class="invalid-feedback" v-if="errors.name">
                  {{ errors.name }}
                </div>
              </div>

              <div class="mb-3">
                <label for="subjectDescription" class="form-label"
                  >Description</label
                >
                <textarea
                  class="form-control"
                  id="subjectDescription"
                  rows="4"
                  v-model="subjectForm.description"
                  :class="{ 'is-invalid': errors.description }"
                ></textarea>
                <div class="invalid-feedback" v-if="errors.description">
                  {{ errors.description }}
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
                @click="closeModal"
              >
                Cancel
              </button>
              <button type="submit" class="btn btn-primary" :disabled="saving">
                <span
                  v-if="saving"
                  class="spinner-border spinner-border-sm me-2"
                ></span>
                {{ editingSubject ? "Update" : "Create" }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
    <div
      v-if="showCreateModal || showEditModal"
      class="modal-backdrop fade show"
      @click="closeModal"
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
            <h5 class="modal-title">Delete Subject</h5>
            <button
              type="button"
              class="btn-close"
              @click="showDeleteModal = false"
            ></button>
          </div>
          <div class="modal-body">
            <p>
              Are you sure you want to delete the subject
              <strong>{{ subjectToDelete?.name }}</strong
              >?
            </p>
            <p class="text-warning">
              This action cannot be undone and will also delete all associated
              chapters and quizzes.
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
              @click="deleteSubject"
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
  name: "SubjectManagement",
  setup() {
    const loading = ref(false);
    const saving = ref(false);
    const deleting = ref(false);
    const subjects = ref([]);
    const searchQuery = ref("");
    const showCreateModal = ref(false);
    const showEditModal = ref(false);
    const showDeleteModal = ref(false);
    const editingSubject = ref(null);
    const subjectToDelete = ref(null);
    const errorMessage = ref("");

    const subjectForm = reactive({
      name: "",
      description: "",
    });

    const errors = reactive({
      name: "",
      description: "",
    });

    const loadSubjects = async () => {
      loading.value = true;
      try {
        const params = {};
        if (searchQuery.value.trim()) {
          params.search = searchQuery.value.trim();
        }

        const response = await api.getSubjects(params);
        subjects.value = response;
      } catch (error) {
        console.error("Error loading subjects:", error);
      } finally {
        loading.value = false;
      }
    };

    const resetFilters = () => {
      searchQuery.value = "";
      loadSubjects();
    };

    const validateForm = () => {
      errors.name = "";
      errors.description = "";

      if (!subjectForm.name.trim()) {
        errors.name = "Subject name is required";
        return false;
      }

      if (subjectForm.name.length < 3 || subjectForm.name.length > 100) {
        errors.name = "Subject name must be between 3 and 100 characters";
        return false;
      }

      return true;
    };

    const saveSubject = async () => {
      if (!validateForm()) return;

      saving.value = true;
      errorMessage.value = "";

      try {
        const data = {
          name: subjectForm.name.trim(),
          description: subjectForm.description.trim(),
        };

        if (editingSubject.value) {
          await api.updateSubject(editingSubject.value.id, data);
        } else {
          await api.createSubject(data);
        }

        closeModal();
        loadSubjects();
      } catch (error) {
        console.error("Error saving subject:", error);
        errorMessage.value =
          error.response?.data?.message || "Failed to save subject";
      } finally {
        saving.value = false;
      }
    };

    const editSubject = (subject) => {
      editingSubject.value = subject;
      subjectForm.name = subject.name;
      subjectForm.description = subject.description || "";
      showEditModal.value = true;
    };

    const confirmDelete = (subject) => {
      subjectToDelete.value = subject;
      showDeleteModal.value = true;
    };

    const deleteSubject = async () => {
      deleting.value = true;

      try {
        await api.deleteSubject(subjectToDelete.value.id);
        showDeleteModal.value = false;
        loadSubjects();
      } catch (error) {
        console.error("Error deleting subject:", error);
        alert("Failed to delete subject. It may have associated chapters.");
      } finally {
        deleting.value = false;
      }
    };

    const closeModal = () => {
      showCreateModal.value = false;
      showEditModal.value = false;
      editingSubject.value = null;
      subjectForm.name = "";
      subjectForm.description = "";
      errorMessage.value = "";
      Object.keys(errors).forEach((key) => (errors[key] = ""));
    };

    const formatDate = (dateString) => {
      if (!dateString) return "";
      return new Date(dateString).toLocaleDateString();
    };

    onMounted(() => {
      loadSubjects();
    });

    return {
      loading,
      saving,
      deleting,
      subjects,
      searchQuery,
      showCreateModal,
      showEditModal,
      showDeleteModal,
      editingSubject,
      subjectToDelete,
      subjectForm,
      errors,
      errorMessage,
      loadSubjects,
      resetFilters,
      saveSubject,
      editSubject,
      confirmDelete,
      deleteSubject,
      closeModal,
      formatDate,
    };
  },
};
</script>

<style scoped>
/* Ensure text visibility in all themes */
.card {
  background-color: var(--bs-body-bg);
  color: var(--bs-body-color);
}

.card-header {
  background-color: var(--bs-secondary-bg);
  color: var(--bs-body-color);
  border-bottom: 1px solid var(--bs-border-color);
}

.form-control {
  background-color: var(--bs-body-bg);
  color: var(--bs-body-color);
  border-color: var(--bs-border-color);
}

.form-control:focus {
  background-color: var(--bs-body-bg);
  color: var(--bs-body-color);
  border-color: var(--bs-primary);
  box-shadow: 0 0 0 0.25rem rgba(var(--bs-primary-rgb), 0.25);
}

.table {
  color: var(--bs-body-color);
}

.table th {
  background-color: var(--bs-secondary-bg);
  color: var(--bs-body-color);
  border-color: var(--bs-border-color);
}

.table td {
  border-color: var(--bs-border-color);
}

.modal-content {
  background-color: var(--bs-body-bg);
  color: var(--bs-body-color);
}

.modal-header {
  background-color: var(--bs-secondary-bg);
  color: var(--bs-body-color);
  border-bottom: 1px solid var(--bs-border-color);
}

.modal-footer {
  background-color: var(--bs-secondary-bg);
  border-top: 1px solid var(--bs-border-color);
}

/* Dark theme specific adjustments */
@media (prefers-color-scheme: dark) {
  .card {
    background-color: #212529;
    color: #ffffff;
  }

  .card-header {
    background-color: #343a40;
    color: #ffffff;
  }

  .form-control {
    background-color: #212529;
    color: #ffffff;
    border-color: #495057;
  }

  .table {
    color: #ffffff;
  }

  .table th {
    background-color: #343a40;
    color: #ffffff;
  }

  .modal-content {
    background-color: #212529;
    color: #ffffff;
  }

  .modal-header {
    background-color: #343a40;
    color: #ffffff;
  }

  .modal-footer {
    background-color: #343a40;
  }
}

/* Light theme specific adjustments */
@media (prefers-color-scheme: light) {
  .card {
    background-color: #ffffff;
    color: #212529;
  }

  .card-header {
    background-color: #f8f9fa;
    color: #212529;
  }

  .form-control {
    background-color: #ffffff;
    color: #212529;
    border-color: #ced4da;
  }

  .table {
    color: #212529;
  }

  .table th {
    background-color: #f8f9fa;
    color: #212529;
  }

  .modal-content {
    background-color: #ffffff;
    color: #212529;
  }

  .modal-header {
    background-color: #f8f9fa;
    color: #212529;
  }

  .modal-footer {
    background-color: #f8f9fa;
  }
}
</style>
