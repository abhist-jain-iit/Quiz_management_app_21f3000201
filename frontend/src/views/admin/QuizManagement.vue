<template>
  <div class="container-fluid">
    <div class="row">
      <div class="col-12">
        <div class="d-flex justify-content-between align-items-center mb-4">
          <h2 class="mb-0">
            <i class="bi bi-clipboard-check me-2"></i>
            Quiz Management
          </h2>
          <button class="btn btn-primary" @click="showCreateModal = true">
            <i class="bi bi-plus-circle me-2"></i>
            Add Quiz
          </button>
        </div>

        <!-- Search and Filter -->
        <div class="card mb-4">
          <div class="card-body">
            <div class="row g-3">
              <div class="col-md-3">
                <input
                  type="text"
                  class="form-control"
                  placeholder="Search quizzes..."
                  v-model="searchQuery"
                  @input="loadQuizzes"
                >
              </div>
              <div class="col-md-3">
                <select class="form-select" v-model="chapterFilter" @change="loadQuizzes">
                  <option value="">All Chapters</option>
                  <option v-for="chapter in chapters" :key="chapter.id" :value="chapter.id">
                    {{ chapter.subject_name }} - {{ chapter.name }}
                  </option>
                </select>
              </div>
              <div class="col-md-2">
                <select class="form-select" v-model="statusFilter" @change="loadQuizzes">
                  <option value="">All Status</option>
                  <option value="true">Active</option>
                  <option value="false">Inactive</option>
                </select>
              </div>
              <div class="col-md-2">
                <button class="btn btn-outline-primary" @click="loadQuizzes">
                  <i class="bi bi-search me-2"></i>
                  Search
                </button>
              </div>
              <div class="col-md-2">
                <button class="btn btn-outline-secondary" @click="resetFilters">
                  <i class="bi bi-arrow-clockwise me-2"></i>
                  Reset
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Quizzes Table -->
        <div class="card">
          <div class="card-header">
            <h5 class="mb-0">Quizzes ({{ quizzes.length }})</h5>
          </div>
          <div class="card-body">
            <div v-if="loading" class="text-center py-4">
              <div class="spinner-border" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>

            <div v-else-if="quizzes.length === 0" class="text-center py-4 text-muted">
              <i class="bi bi-clipboard-x fs-1 mb-3"></i>
              <p>No quizzes found</p>
            </div>

            <div v-else class="table-responsive">
              <table class="table table-striped table-hover">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Title</th>
                    <th>Chapter</th>
                    <th>Date</th>
                    <th>Duration</th>
                    <th>Questions</th>
                    <th>Status</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="quiz in quizzes" :key="quiz.id">
                    <td>{{ quiz.id }}</td>
                    <td><strong>{{ quiz.title }}</strong></td>
                    <td>
                      <div>
                        <span class="badge bg-primary">{{ quiz.subject_name }}</span>
                        <br>
                        <small class="text-muted">{{ quiz.chapter_name }}</small>
                      </div>
                    </td>
                    <td>{{ formatDate(quiz.date_of_quiz) }}</td>
                    <td>{{ quiz.time_duration }}</td>
                    <td>
                      <span class="badge bg-info">{{ quiz.question_count }} questions</span>
                    </td>
                    <td>
                      <span class="badge" :class="quiz.is_active ? 'bg-success' : 'bg-secondary'">
                        {{ quiz.is_active ? 'Active' : 'Inactive' }}
                      </span>
                    </td>
                    <td>
                      <div class="btn-group btn-group-sm">
                        <router-link :to="`/admin/questions?quiz_id=${quiz.id}`" class="btn btn-outline-info">
                          <i class="bi bi-question-circle"></i>
                        </router-link>
                        <button class="btn btn-outline-primary" @click="editQuiz(quiz)">
                          <i class="bi bi-pencil"></i>
                        </button>
                        <button class="btn btn-outline-danger" @click="confirmDelete(quiz)">
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

    <!-- Create/Edit Quiz Modal -->
    <div class="modal fade" :class="{ show: showCreateModal || showEditModal }" :style="{ display: (showCreateModal || showEditModal) ? 'block' : 'none' }" tabindex="-1">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ editingQuiz ? 'Edit Quiz' : 'Create Quiz' }}</h5>
            <button type="button" class="btn-close" @click="closeModal"></button>
          </div>
          <form @submit.prevent="saveQuiz">
            <div class="modal-body">
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label for="quizTitle" class="form-label">Quiz Title *</label>
                  <input
                    type="text"
                    class="form-control"
                    id="quizTitle"
                    v-model="quizForm.title"
                    :class="{ 'is-invalid': errors.title }"
                    required
                  >
                  <div class="invalid-feedback" v-if="errors.title">
                    {{ errors.title }}
                  </div>
                </div>

                <div class="col-md-6 mb-3">
                  <label for="chapterSelect" class="form-label">Chapter *</label>
                  <select
                    class="form-select"
                    id="chapterSelect"
                    v-model="quizForm.chapter_id"
                    :class="{ 'is-invalid': errors.chapter_id }"
                    required
                  >
                    <option value="">Select Chapter</option>
                    <option v-for="chapter in chapters" :key="chapter.id" :value="chapter.id">
                      {{ chapter.subject_name }} - {{ chapter.name }}
                    </option>
                  </select>
                  <div class="invalid-feedback" v-if="errors.chapter_id">
                    {{ errors.chapter_id }}
                  </div>
                </div>
              </div>

              <div class="row">
                <div class="col-md-6 mb-3">
                  <label for="quizDate" class="form-label">Quiz Date *</label>
                  <input
                    type="date"
                    class="form-control"
                    id="quizDate"
                    v-model="quizForm.date_of_quiz"
                    :class="{ 'is-invalid': errors.date_of_quiz }"
                    required
                  >
                  <div class="invalid-feedback" v-if="errors.date_of_quiz">
                    {{ errors.date_of_quiz }}
                  </div>
                </div>

                <div class="col-md-6 mb-3">
                  <label for="timeDuration" class="form-label">Duration (HH:MM) *</label>
                  <input
                    type="time"
                    class="form-control"
                    id="timeDuration"
                    v-model="quizForm.time_duration"
                    :class="{ 'is-invalid': errors.time_duration }"
                    required
                  >
                  <div class="invalid-feedback" v-if="errors.time_duration">
                    {{ errors.time_duration }}
                  </div>
                </div>
              </div>

              <div class="mb-3">
                <label for="quizRemarks" class="form-label">Remarks</label>
                <textarea
                  class="form-control"
                  id="quizRemarks"
                  rows="3"
                  v-model="quizForm.remarks"
                  :class="{ 'is-invalid': errors.remarks }"
                ></textarea>
                <div class="invalid-feedback" v-if="errors.remarks">
                  {{ errors.remarks }}
                </div>
              </div>

              <div class="mb-3">
                <div class="form-check">
                  <input
                    class="form-check-input"
                    type="checkbox"
                    id="isActive"
                    v-model="quizForm.is_active"
                  >
                  <label class="form-check-label" for="isActive">
                    Active Quiz
                  </label>
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
                {{ editingQuiz ? 'Update' : 'Create' }}
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
            <h5 class="modal-title">Delete Quiz</h5>
            <button type="button" class="btn-close" @click="showDeleteModal = false"></button>
          </div>
          <div class="modal-body">
            <p>Are you sure you want to delete the quiz <strong>{{ quizToDelete?.title }}</strong>?</p>
            <p class="text-warning">This action cannot be undone and will also delete all associated questions and scores.</p>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="showDeleteModal = false">Cancel</button>
            <button type="button" class="btn btn-danger" @click="deleteQuiz" :disabled="deleting">
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
  name: 'QuizManagement',
  setup() {
    const loading = ref(false)
    const saving = ref(false)
    const deleting = ref(false)
    const quizzes = ref([])
    const chapters = ref([])
    const searchQuery = ref('')
    const chapterFilter = ref('')
    const statusFilter = ref('')
    const showCreateModal = ref(false)
    const showEditModal = ref(false)
    const showDeleteModal = ref(false)
    const editingQuiz = ref(null)
    const quizToDelete = ref(null)
    const errorMessage = ref('')

    const quizForm = reactive({
      title: '',
      chapter_id: '',
      date_of_quiz: '',
      time_duration: '',
      remarks: '',
      is_active: true
    })

    const errors = reactive({
      title: '',
      chapter_id: '',
      date_of_quiz: '',
      time_duration: '',
      remarks: ''
    })

    const loadQuizzes = async () => {
      loading.value = true
      try {
        const params = {}
        if (searchQuery.value.trim()) {
          params.search = searchQuery.value.trim()
        }
        if (chapterFilter.value) {
          params.chapter_id = chapterFilter.value
        }
        if (statusFilter.value) {
          params.is_active = statusFilter.value
        }
        
        const response = await api.getQuizzes(params)
        quizzes.value = response
      } catch (error) {
        console.error('Error loading quizzes:', error)
      } finally {
        loading.value = false
      }
    }

    const loadChapters = async () => {
      try {
        const response = await api.getChapters()
        chapters.value = response
      } catch (error) {
        console.error('Error loading chapters:', error)
      }
    }

    const resetFilters = () => {
      searchQuery.value = ''
      chapterFilter.value = ''
      statusFilter.value = ''
      loadQuizzes()
    }

    const validateForm = () => {
      Object.keys(errors).forEach(key => errors[key] = '')
      
      if (!quizForm.title.trim()) {
        errors.title = 'Quiz title is required'
        return false
      }
      
      if (!quizForm.chapter_id) {
        errors.chapter_id = 'Chapter is required'
        return false
      }
      
      if (!quizForm.date_of_quiz) {
        errors.date_of_quiz = 'Quiz date is required'
        return false
      }
      
      if (!quizForm.time_duration) {
        errors.time_duration = 'Duration is required'
        return false
      }
      
      return true
    }

    const saveQuiz = async () => {
      if (!validateForm()) return
      
      saving.value = true
      errorMessage.value = ''
      
      try {
        const data = {
          title: quizForm.title.trim(),
          chapter_id: parseInt(quizForm.chapter_id),
          date_of_quiz: quizForm.date_of_quiz,
          time_duration: quizForm.time_duration,
          remarks: quizForm.remarks.trim(),
          is_active: quizForm.is_active
        }
        
        if (editingQuiz.value) {
          await api.updateQuiz(editingQuiz.value.id, data)
        } else {
          await api.createQuiz(data)
        }
        
        closeModal()
        loadQuizzes()
      } catch (error) {
        console.error('Error saving quiz:', error)
        errorMessage.value = error.response?.data?.message || 'Failed to save quiz'
      } finally {
        saving.value = false
      }
    }

    const editQuiz = (quiz) => {
      editingQuiz.value = quiz
      quizForm.title = quiz.title
      quizForm.chapter_id = quiz.chapter_id
      quizForm.date_of_quiz = quiz.date_of_quiz
      quizForm.time_duration = quiz.time_duration
      quizForm.remarks = quiz.remarks || ''
      quizForm.is_active = quiz.is_active
      showEditModal.value = true
    }

    const confirmDelete = (quiz) => {
      quizToDelete.value = quiz
      showDeleteModal.value = true
    }

    const deleteQuiz = async () => {
      deleting.value = true
      
      try {
        await api.deleteQuiz(quizToDelete.value.id)
        showDeleteModal.value = false
        loadQuizzes()
      } catch (error) {
        console.error('Error deleting quiz:', error)
        alert('Failed to delete quiz.')
      } finally {
        deleting.value = false
      }
    }

    const closeModal = () => {
      showCreateModal.value = false
      showEditModal.value = false
      editingQuiz.value = null
      Object.keys(quizForm).forEach(key => {
        if (key === 'is_active') {
          quizForm[key] = true
        } else {
          quizForm[key] = ''
        }
      })
      errorMessage.value = ''
      Object.keys(errors).forEach(key => errors[key] = '')
    }

    const formatDate = (dateString) => {
      if (!dateString) return ''
      return new Date(dateString).toLocaleDateString()
    }

    onMounted(() => {
      loadChapters()
      loadQuizzes()
    })

    return {
      loading,
      saving,
      deleting,
      quizzes,
      chapters,
      searchQuery,
      chapterFilter,
      statusFilter,
      showCreateModal,
      showEditModal,
      showDeleteModal,
      editingQuiz,
      quizToDelete,
      quizForm,
      errors,
      errorMessage,
      loadQuizzes,
      resetFilters,
      saveQuiz,
      editQuiz,
      confirmDelete,
      deleteQuiz,
      closeModal,
      formatDate
    }
  }
}
</script>
