<template>
  <div class="container-fluid">
    <div class="row">
      <div class="col-12">
        <div class="d-flex justify-content-between align-items-center mb-4">
          <h2 class="mb-0">
            <i class="bi bi-question-circle me-2"></i>
            Question Management
          </h2>
          <button class="btn btn-primary" @click="showCreateModal = true">
            <i class="bi bi-plus-circle me-2"></i>
            Add Question
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
                  placeholder="Search questions..."
                  v-model="searchQuery"
                  @input="loadQuestions"
                />
              </div>
              <div class="col-md-4">
                <select
                  class="form-select"
                  v-model="quizFilter"
                  @change="loadQuestions"
                >
                  <option value="">All Quizzes</option>
                  <option
                    v-for="quiz in quizzes"
                    :key="quiz.id"
                    :value="quiz.id"
                  >
                    {{ quiz.title }} ({{ quiz.subject_name }} -
                    {{ quiz.chapter_name }})
                  </option>
                </select>
              </div>
              <div class="col-md-2">
                <button class="btn btn-outline-primary" @click="loadQuestions">
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

        <!-- Questions Table -->
        <div class="card">
          <div class="card-header">
            <h5 class="mb-0">Questions ({{ questions.length }})</h5>
          </div>
          <div class="card-body">
            <div v-if="loading" class="text-center py-4">
              <div class="spinner-border" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>

            <div
              v-else-if="questions.length === 0"
              class="text-center py-4 text-muted"
            >
              <i class="bi bi-question-diamond fs-1 mb-3"></i>
              <p>No questions found</p>
            </div>

            <div v-else>
              <div
                v-for="question in questions"
                :key="question.id"
                class="card mb-3"
              >
                <div class="card-body">
                  <div
                    class="d-flex justify-content-between align-items-start mb-3"
                  >
                    <h6 class="card-title mb-0">Question #{{ question.id }}</h6>
                    <div class="btn-group btn-group-sm">
                      <button
                        class="btn btn-outline-primary"
                        @click="editQuestion(question)"
                      >
                        <i class="bi bi-pencil"></i>
                      </button>
                      <button
                        class="btn btn-outline-danger"
                        @click="confirmDelete(question)"
                      >
                        <i class="bi bi-trash"></i>
                      </button>
                    </div>
                  </div>

                  <p class="card-text">
                    <strong>{{ question.question_statement }}</strong>
                  </p>

                  <div class="row g-2 mb-3">
                    <div class="col-md-6">
                      <div class="form-check">
                        <input
                          class="form-check-input"
                          type="radio"
                          disabled
                          :checked="question.correct_option === 1"
                        />
                        <label class="form-check-label">
                          A) {{ question.option1 }}
                        </label>
                      </div>
                    </div>
                    <div class="col-md-6">
                      <div class="form-check">
                        <input
                          class="form-check-input"
                          type="radio"
                          disabled
                          :checked="question.correct_option === 2"
                        />
                        <label class="form-check-label">
                          B) {{ question.option2 }}
                        </label>
                      </div>
                    </div>
                    <div class="col-md-6" v-if="question.option3">
                      <div class="form-check">
                        <input
                          class="form-check-input"
                          type="radio"
                          disabled
                          :checked="question.correct_option === 3"
                        />
                        <label class="form-check-label">
                          C) {{ question.option3 }}
                        </label>
                      </div>
                    </div>
                    <div class="col-md-6" v-if="question.option4">
                      <div class="form-check">
                        <input
                          class="form-check-input"
                          type="radio"
                          disabled
                          :checked="question.correct_option === 4"
                        />
                        <label class="form-check-label">
                          D) {{ question.option4 }}
                        </label>
                      </div>
                    </div>
                  </div>

                  <div
                    class="d-flex justify-content-between align-items-center"
                  >
                    <small class="text-muted">
                      Quiz: {{ getQuizTitle(question.quiz_id) }} | Marks:
                      {{ question.marks }} | Correct: Option
                      {{ question.correct_option }}
                    </small>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Create/Edit Question Modal -->
    <div
      class="modal fade"
      :class="{ show: showCreateModal || showEditModal }"
      :style="{ display: showCreateModal || showEditModal ? 'block' : 'none' }"
      tabindex="-1"
    >
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">
              {{ editingQuestion ? "Edit Question" : "Create Question" }}
            </h5>
            <button
              type="button"
              class="btn-close"
              @click="closeModal"
            ></button>
          </div>
          <form @submit.prevent="saveQuestion">
            <div class="modal-body">
              <div class="mb-3">
                <label for="quizSelect" class="form-label">Quiz *</label>
                <select
                  class="form-select"
                  id="quizSelect"
                  v-model="questionForm.quiz_id"
                  :class="{ 'is-invalid': errors.quiz_id }"
                  required
                >
                  <option value="">Select Quiz</option>
                  <option
                    v-for="quiz in quizzes"
                    :key="quiz.id"
                    :value="quiz.id"
                  >
                    {{ quiz.title }} ({{ quiz.subject_name }} -
                    {{ quiz.chapter_name }})
                  </option>
                </select>
                <div class="invalid-feedback" v-if="errors.quiz_id">
                  {{ errors.quiz_id }}
                </div>
              </div>

              <div class="mb-3">
                <label for="questionStatement" class="form-label"
                  >Question Statement *</label
                >
                <textarea
                  class="form-control"
                  id="questionStatement"
                  rows="3"
                  v-model="questionForm.question_statement"
                  :class="{ 'is-invalid': errors.question_statement }"
                  required
                ></textarea>
                <div class="invalid-feedback" v-if="errors.question_statement">
                  {{ errors.question_statement }}
                </div>
              </div>

              <div class="row">
                <div class="col-md-6 mb-3">
                  <label for="option1" class="form-label">Option A *</label>
                  <input
                    type="text"
                    class="form-control"
                    id="option1"
                    v-model="questionForm.option1"
                    :class="{ 'is-invalid': errors.option1 }"
                    required
                  />
                  <div class="invalid-feedback" v-if="errors.option1">
                    {{ errors.option1 }}
                  </div>
                </div>

                <div class="col-md-6 mb-3">
                  <label for="option2" class="form-label">Option B *</label>
                  <input
                    type="text"
                    class="form-control"
                    id="option2"
                    v-model="questionForm.option2"
                    :class="{ 'is-invalid': errors.option2 }"
                    required
                  />
                  <div class="invalid-feedback" v-if="errors.option2">
                    {{ errors.option2 }}
                  </div>
                </div>
              </div>

              <div class="row">
                <div class="col-md-6 mb-3">
                  <label for="option3" class="form-label">Option C</label>
                  <input
                    type="text"
                    class="form-control"
                    id="option3"
                    v-model="questionForm.option3"
                  />
                </div>

                <div class="col-md-6 mb-3">
                  <label for="option4" class="form-label">Option D</label>
                  <input
                    type="text"
                    class="form-control"
                    id="option4"
                    v-model="questionForm.option4"
                  />
                </div>
              </div>

              <div class="row">
                <div class="col-md-6 mb-3">
                  <label for="correctOption" class="form-label"
                    >Correct Option *</label
                  >
                  <select
                    class="form-select"
                    id="correctOption"
                    v-model="questionForm.correct_option"
                    :class="{ 'is-invalid': errors.correct_option }"
                    required
                  >
                    <option value="">Select Correct Option</option>
                    <option value="1">A</option>
                    <option value="2">B</option>
                    <option value="3" v-if="questionForm.option3">C</option>
                    <option value="4" v-if="questionForm.option4">D</option>
                  </select>
                  <div class="invalid-feedback" v-if="errors.correct_option">
                    {{ errors.correct_option }}
                  </div>
                </div>

                <div class="col-md-6 mb-3">
                  <label for="marks" class="form-label">Marks</label>
                  <input
                    type="number"
                    class="form-control"
                    id="marks"
                    v-model="questionForm.marks"
                    min="1"
                    max="10"
                  />
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
                {{ editingQuestion ? "Update" : "Create" }}
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
            <h5 class="modal-title">Delete Question</h5>
            <button
              type="button"
              class="btn-close"
              @click="showDeleteModal = false"
            ></button>
          </div>
          <div class="modal-body">
            <p>Are you sure you want to delete this question?</p>
            <p class="text-warning">This action cannot be undone.</p>
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
              @click="deleteQuestion"
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
import { ref, reactive, onMounted, computed } from "vue";
import { useRoute } from "vue-router";
import api from "../../services/api";

export default {
  name: "QuestionManagement",
  setup() {
    const route = useRoute();
    const loading = ref(false);
    const saving = ref(false);
    const deleting = ref(false);
    const questions = ref([]);
    const quizzes = ref([]);
    const searchQuery = ref("");
    const quizFilter = ref("");
    const showCreateModal = ref(false);
    const showEditModal = ref(false);
    const showDeleteModal = ref(false);
    const editingQuestion = ref(null);
    const questionToDelete = ref(null);
    const errorMessage = ref("");

    const questionForm = reactive({
      quiz_id: "",
      question_statement: "",
      option1: "",
      option2: "",
      option3: "",
      option4: "",
      correct_option: "",
      marks: 1,
    });

    const errors = reactive({
      quiz_id: "",
      question_statement: "",
      option1: "",
      option2: "",
      correct_option: "",
    });

    const getQuizTitle = (quizId) => {
      const quiz = quizzes.value.find((q) => q.id === quizId);
      return quiz ? quiz.title : "Unknown Quiz";
    };

    const loadQuestions = async () => {
      loading.value = true;
      try {
        const params = {};
        if (searchQuery.value.trim()) {
          params.search = searchQuery.value.trim();
        }
        if (quizFilter.value) {
          params.quiz_id = quizFilter.value;
        }

        const response = await api.getQuestions(params);
        questions.value = response;
      } catch (error) {
        console.error("Error loading questions:", error);
      } finally {
        loading.value = false;
      }
    };

    const loadQuizzes = async () => {
      try {
        const response = await api.getQuizzes();
        quizzes.value = response;
      } catch (error) {
        console.error("Error loading quizzes:", error);
      }
    };

    const resetFilters = () => {
      searchQuery.value = "";
      quizFilter.value = "";
      loadQuestions();
    };

    const validateForm = () => {
      Object.keys(errors).forEach((key) => (errors[key] = ""));

      if (!questionForm.quiz_id) {
        errors.quiz_id = "Quiz is required";
        return false;
      }

      if (!questionForm.question_statement.trim()) {
        errors.question_statement = "Question statement is required";
        return false;
      }

      if (!questionForm.option1.trim()) {
        errors.option1 = "Option A is required";
        return false;
      }

      if (!questionForm.option2.trim()) {
        errors.option2 = "Option B is required";
        return false;
      }

      if (!questionForm.correct_option) {
        errors.correct_option = "Correct option is required";
        return false;
      }

      return true;
    };

    const saveQuestion = async () => {
      if (!validateForm()) return;

      saving.value = true;
      errorMessage.value = "";

      try {
        const data = {
          quiz_id: parseInt(questionForm.quiz_id),
          question_statement: questionForm.question_statement.trim(),
          option1: questionForm.option1.trim(),
          option2: questionForm.option2.trim(),
          option3: questionForm.option3.trim() || null,
          option4: questionForm.option4.trim() || null,
          correct_option: parseInt(questionForm.correct_option),
          marks: questionForm.marks,
        };

        if (editingQuestion.value) {
          await api.updateQuestion(editingQuestion.value.id, data);
        } else {
          await api.createQuestion(data);
        }

        closeModal();
        loadQuestions();
      } catch (error) {
        console.error("Error saving question:", error);
        errorMessage.value =
          error.response?.data?.message || "Failed to save question";
      } finally {
        saving.value = false;
      }
    };

    const editQuestion = (question) => {
      editingQuestion.value = question;
      questionForm.quiz_id = question.quiz_id;
      questionForm.question_statement = question.question_statement;
      questionForm.option1 = question.option1;
      questionForm.option2 = question.option2;
      questionForm.option3 = question.option3 || "";
      questionForm.option4 = question.option4 || "";
      questionForm.correct_option = question.correct_option.toString();
      questionForm.marks = question.marks;
      showEditModal.value = true;
    };

    const confirmDelete = (question) => {
      questionToDelete.value = question;
      showDeleteModal.value = true;
    };

    const deleteQuestion = async () => {
      deleting.value = true;

      try {
        await api.deleteQuestion(questionToDelete.value.id);
        showDeleteModal.value = false;
        loadQuestions();
      } catch (error) {
        console.error("Error deleting question:", error);
        alert("Failed to delete question.");
      } finally {
        deleting.value = false;
      }
    };

    const closeModal = () => {
      showCreateModal.value = false;
      showEditModal.value = false;
      editingQuestion.value = null;
      Object.keys(questionForm).forEach((key) => {
        if (key === "marks") {
          questionForm[key] = 1;
        } else {
          questionForm[key] = "";
        }
      });
      errorMessage.value = "";
      Object.keys(errors).forEach((key) => (errors[key] = ""));
    };

    onMounted(() => {
      // Check if quiz_id is provided in query params
      if (route.query.quiz_id) {
        quizFilter.value = route.query.quiz_id;
      }

      loadQuizzes();
      loadQuestions();
    });

    return {
      loading,
      saving,
      deleting,
      questions,
      quizzes,
      searchQuery,
      quizFilter,
      showCreateModal,
      showEditModal,
      showDeleteModal,
      editingQuestion,
      questionToDelete,
      questionForm,
      errors,
      errorMessage,
      getQuizTitle,
      loadQuestions,
      resetFilters,
      saveQuestion,
      editQuestion,
      confirmDelete,
      deleteQuestion,
      closeModal,
    };
  },
};
</script>
