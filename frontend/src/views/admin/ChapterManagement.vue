<template>
  <div class="container-fluid">
    <div class="row">
      <div class="col-12">
        <div class="d-flex justify-content-between align-items-center mb-4">
          <h2 class="mb-0">
            <i class="bi bi-book me-2"></i>
            Chapter Management
          </h2>
          <button class="btn btn-primary" @click="showCreateModal = true">
            <i class="bi bi-plus-circle me-2"></i>
            Add Chapter
          </button>
        </div>

        <!-- Search and Filter -->
        <div class="card mb-4">
          <div class="card-body">
            <div class="row g-3">
              <div class="col-md-4">
                <input
                  type="text"
                  class="form-control"
                  placeholder="Search chapters..."
                  v-model="searchQuery"
                  @input="loadChapters"
                >
              </div>
              <div class="col-md-3">
                <select class="form-select" v-model="subjectFilter" @change="loadChapters">
                  <option value="">All Subjects</option>
                  <option v-for="subject in subjects" :key="subject.id" :value="subject.id">
                    {{ subject.name }}
                  </option>
                </select>
              </div>
              <div class="col-md-2">
                <button class="btn btn-outline-primary" @click="loadChapters">
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

        <!-- Chapters Table -->
        <div class="card">
          <div class="card-header">
            <h5 class="mb-0">Chapters ({{ chapters.length }})</h5>
          </div>
          <div class="card-body">
            <div v-if="loading" class="text-center py-4">
              <div class="spinner-border" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>

            <div v-else-if="chapters.length === 0" class="text-center py-4 text-muted">
              <i class="bi bi-book-half fs-1 mb-3"></i>
              <p>No chapters found</p>
            </div>

            <div v-else class="table-responsive">
              <table class="table table-striped table-hover">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>Subject</th>
                    <th>Description</th>
                    <th>Quizzes</th>
                    <th>Created</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="chapter in chapters" :key="chapter.id">
                    <td>{{ chapter.id }}</td>
                    <td><strong>{{ chapter.name }}</strong></td>
                    <td>
                      <span class="badge bg-primary">{{ chapter.subject_name }}</span>
                    </td>
                    <td>
                      <span v-if="chapter.description">{{ chapter.description.substring(0, 100) }}{{ chapter.description.length > 100 ? '...' : '' }}</span>
                      <span v-else class="text-muted">No description</span>
                    </td>
                    <td>
                      <span class="badge bg-info">{{ chapter.quiz_count || 0 }} quizzes</span>
                    </td>
                    <td>{{ formatDate(chapter.created_at) }}</td>
                    <td>
                      <div class="btn-group btn-group-sm">
                        <button class="btn btn-outline-primary" @click="editChapter(chapter)">
                          <i class="bi bi-pencil"></i>
                        </button>
                        <button class="btn btn-outline-danger" @click="confirmDelete(chapter)">
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

    <!-- Create/Edit Chapter Modal -->
    <div class="modal fade" :class="{ show: showCreateModal || showEditModal }" :style="{ display: (showCreateModal || showEditModal) ? 'block' : 'none' }" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ editingChapter ? 'Edit Chapter' : 'Create Chapter' }}</h5>
            <button type="button" class="btn-close" @click="closeModal"></button>
          </div>
          <form @submit.prevent="saveChapter">
            <div class="modal-body">
              <div class="mb-3">
                <label for="subjectSelect" class="form-label">Subject *</label>
                <select
                  class="form-select"
                  id="subjectSelect"
                  v-model="chapterForm.subject_id"
                  :class="{ 'is-invalid': errors.subject_id }"
                  required
                >
                  <option value="">Select Subject</option>
                  <option v-for="subject in subjects" :key="subject.id" :value="subject.id">
                    {{ subject.name }}
                  </option>
                </select>
                <div class="invalid-feedback" v-if="errors.subject_id">
                  {{ errors.subject_id }}
                </div>
              </div>

              <div class="mb-3">
                <label for="chapterName" class="form-label">Chapter Name *</label>
                <input
                  type="text"
                  class="form-control"
                  id="chapterName"
                  v-model="chapterForm.name"
                  :class="{ 'is-invalid': errors.name }"
                  required
                >
                <div class="invalid-feedback" v-if="errors.name">
                  {{ errors.name }}
                </div>
              </div>

              <div class="mb-3">
                <label for="chapterDescription" class="form-label">Description</label>
                <textarea
                  class="form-control"
                  id="chapterDescription"
                  rows="4"
                  v-model="chapterForm.description"
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
              <button type="button" class="btn btn-secondary" @click="closeModal">Cancel</button>
              <button type="submit" class="btn btn-primary" :disabled="saving">
                <span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>
                {{ editingChapter ? 'Update' : 'Create' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
    <div v-if="showCreateModal || showEditModal" class="modal-backdrop fade show" @click="closeModal"></div>

    <!-- Delete Confirmation Modal -->
    <div class="modal fade" :class="{ show: showDeleteModal }" :style="{ display: showDeleteModal ? 'block' : 'none' }" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Delete Chapter</h5>
            <button type="button" class="btn-close" @click="showDeleteModal = false"></button>
          </div>
          <div class="modal-body">
            <p>Are you sure you want to delete the chapter <strong>{{ chapterToDelete?.name }}</strong>?</p>
            <p class="text-warning">This action cannot be undone and will also delete all associated quizzes.</p>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="showDeleteModal = false">Cancel</button>
            <button type="button" class="btn btn-danger" @click="deleteChapter" :disabled="deleting">
              <span v-if="deleting" class="spinner-border spinner-border-sm me-2"></span>
              Delete
            </button>
          </div>
        </div>
      </div>
    </div>
    <div v-if="showDeleteModal" class="modal-backdrop fade show" @click="showDeleteModal = false"></div>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import api from '../../services/api'

export default {
  name: 'ChapterManagement',
  setup() {
    const loading = ref(false)
    const saving = ref(false)
    const deleting = ref(false)
    const chapters = ref([])
    const subjects = ref([])
    const searchQuery = ref('')
    const subjectFilter = ref('')
    const showCreateModal = ref(false)
    const showEditModal = ref(false)
    const showDeleteModal = ref(false)
    const editingChapter = ref(null)
    const chapterToDelete = ref(null)
    const errorMessage = ref('')

    const chapterForm = reactive({
      name: '',
      description: '',
      subject_id: ''
    })

    const errors = reactive({
      name: '',
      description: '',
      subject_id: ''
    })

    const loadChapters = async () => {
      loading.value = true
      try {
        const params = {}
        if (searchQuery.value.trim()) {
          params.search = searchQuery.value.trim()
        }
        if (subjectFilter.value) {
          params.subject_id = subjectFilter.value
        }
        
        const response = await api.getChapters(params)
        chapters.value = response
      } catch (error) {
        console.error('Error loading chapters:', error)
      } finally {
        loading.value = false
      }
    }

    const loadSubjects = async () => {
      try {
        const response = await api.getSubjects()
        subjects.value = response
      } catch (error) {
        console.error('Error loading subjects:', error)
      }
    }

    const resetFilters = () => {
      searchQuery.value = ''
      subjectFilter.value = ''
      loadChapters()
    }

    const validateForm = () => {
      errors.name = ''
      errors.description = ''
      errors.subject_id = ''
      
      if (!chapterForm.name.trim()) {
        errors.name = 'Chapter name is required'
        return false
      }
      
      if (!chapterForm.subject_id) {
        errors.subject_id = 'Subject is required'
        return false
      }
      
      return true
    }

    const saveChapter = async () => {
      if (!validateForm()) return
      
      saving.value = true
      errorMessage.value = ''
      
      try {
        const data = {
          name: chapterForm.name.trim(),
          description: chapterForm.description.trim(),
          subject_id: parseInt(chapterForm.subject_id)
        }
        
        if (editingChapter.value) {
          await api.updateChapter(editingChapter.value.id, data)
        } else {
          await api.createChapter(data)
        }
        
        closeModal()
        loadChapters()
      } catch (error) {
        console.error('Error saving chapter:', error)
        errorMessage.value = error.response?.data?.message || 'Failed to save chapter'
      } finally {
        saving.value = false
      }
    }

    const editChapter = (chapter) => {
      editingChapter.value = chapter
      chapterForm.name = chapter.name
      chapterForm.description = chapter.description || ''
      chapterForm.subject_id = chapter.subject_id
      showEditModal.value = true
    }

    const confirmDelete = (chapter) => {
      chapterToDelete.value = chapter
      showDeleteModal.value = true
    }

    const deleteChapter = async () => {
      deleting.value = true
      
      try {
        await api.deleteChapter(chapterToDelete.value.id)
        showDeleteModal.value = false
        loadChapters()
      } catch (error) {
        console.error('Error deleting chapter:', error)
        alert('Failed to delete chapter. It may have associated quizzes.')
      } finally {
        deleting.value = false
      }
    }

    const closeModal = () => {
      showCreateModal.value = false
      showEditModal.value = false
      editingChapter.value = null
      chapterForm.name = ''
      chapterForm.description = ''
      chapterForm.subject_id = ''
      errorMessage.value = ''
      Object.keys(errors).forEach(key => errors[key] = '')
    }

    const formatDate = (dateString) => {
      if (!dateString) return ''
      return new Date(dateString).toLocaleDateString()
    }

    onMounted(() => {
      loadSubjects()
      loadChapters()
    })

    return {
      loading,
      saving,
      deleting,
      chapters,
      subjects,
      searchQuery,
      subjectFilter,
      showCreateModal,
      showEditModal,
      showDeleteModal,
      editingChapter,
      chapterToDelete,
      chapterForm,
      errors,
      errorMessage,
      loadChapters,
      resetFilters,
      saveChapter,
      editChapter,
      confirmDelete,
      deleteChapter,
      closeModal,
      formatDate
    }
  }
}
</script>
