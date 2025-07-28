<template>
  <div class="container-fluid">
    <!-- Timer Card (Fixed Position) -->
    <div class="quiz-timer" v-if="quiz && !quizCompleted">
      <div class="card border-warning">
        <div class="card-body text-center p-2">
          <h6 class="mb-1">Time Remaining</h6>
          <h4
            class="text-warning mb-0"
            :class="{ 'text-danger': timeRemaining < 300 }"
          >
            {{ formatTime(timeRemaining) }}
          </h4>
        </div>
      </div>
    </div>

    <div class="row" v-if="loading">
      <div class="col-12">
        <div class="loading-spinner">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading quiz...</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Quiz Content -->
    <div class="row" v-else-if="quiz && !quizCompleted">
      <!-- Question Navigation Sidebar -->
      <div class="col-md-3">
        <div class="card sticky-top" style="top: 100px">
          <div class="card-header">
            <h6 class="mb-0">
              <i class="bi bi-list-ol me-2"></i>
              Questions ({{ currentQuestionIndex + 1 }}/{{
                quiz.questions.length
              }})
            </h6>
          </div>
          <div class="card-body question-nav">
            <div class="row g-2">
              <div
                v-for="(question, index) in quiz.questions"
                :key="question.id"
                class="col-4"
              >
                <button
                  class="btn btn-sm w-100"
                  :class="getQuestionButtonClass(index)"
                  @click="goToQuestion(index)"
                >
                  {{ index + 1 }}
                </button>
              </div>
            </div>

            <hr />

            <div class="d-grid gap-2">
              <button class="btn btn-warning" @click="showSubmitConfirm = true">
                <i class="bi bi-check-circle me-2"></i>
                Submit Quiz
              </button>
              <button
                class="btn btn-outline-secondary"
                @click="showExitConfirm = true"
              >
                <i class="bi bi-x-circle me-2"></i>
                Exit Quiz
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Main Question Area -->
      <div class="col-md-9">
        <div class="card">
          <div
            class="card-header d-flex justify-content-between align-items-center"
          >
            <h5 class="mb-0">{{ quiz.title }}</h5>
            <span class="badge bg-primary"
              >Question {{ currentQuestionIndex + 1 }} of
              {{ quiz.questions.length }}</span
            >
          </div>
          <div class="card-body">
            <div v-if="currentQuestion">
              <h6 class="mb-3">{{ currentQuestion.question_statement }}</h6>

              <div class="row g-3">
                <div class="col-md-6" v-if="currentQuestion.option1">
                  <div class="form-check">
                    <input
                      class="form-check-input"
                      type="radio"
                      :name="`question_${currentQuestion.id}`"
                      :id="`option1_${currentQuestion.id}`"
                      :value="1"
                      v-model="answers[currentQuestion.id]"
                    />
                    <label
                      class="form-check-label"
                      :for="`option1_${currentQuestion.id}`"
                    >
                      A) {{ currentQuestion.option1 }}
                    </label>
                  </div>
                </div>

                <div class="col-md-6" v-if="currentQuestion.option2">
                  <div class="form-check">
                    <input
                      class="form-check-input"
                      type="radio"
                      :name="`question_${currentQuestion.id}`"
                      :id="`option2_${currentQuestion.id}`"
                      :value="2"
                      v-model="answers[currentQuestion.id]"
                    />
                    <label
                      class="form-check-label"
                      :for="`option2_${currentQuestion.id}`"
                    >
                      B) {{ currentQuestion.option2 }}
                    </label>
                  </div>
                </div>

                <div class="col-md-6" v-if="currentQuestion.option3">
                  <div class="form-check">
                    <input
                      class="form-check-input"
                      type="radio"
                      :name="`question_${currentQuestion.id}`"
                      :id="`option3_${currentQuestion.id}`"
                      :value="3"
                      v-model="answers[currentQuestion.id]"
                    />
                    <label
                      class="form-check-label"
                      :for="`option3_${currentQuestion.id}`"
                    >
                      C) {{ currentQuestion.option3 }}
                    </label>
                  </div>
                </div>

                <div class="col-md-6" v-if="currentQuestion.option4">
                  <div class="form-check">
                    <input
                      class="form-check-input"
                      type="radio"
                      :name="`question_${currentQuestion.id}`"
                      :id="`option4_${currentQuestion.id}`"
                      :value="4"
                      v-model="answers[currentQuestion.id]"
                    />
                    <label
                      class="form-check-label"
                      :for="`option4_${currentQuestion.id}`"
                    >
                      D) {{ currentQuestion.option4 }}
                    </label>
                  </div>
                </div>
              </div>

              <div class="d-flex justify-content-between mt-4">
                <button
                  class="btn btn-outline-primary"
                  @click="previousQuestion"
                  :disabled="currentQuestionIndex === 0"
                >
                  <i class="bi bi-arrow-left me-2"></i>
                  Previous
                </button>

                <button
                  class="btn btn-primary"
                  @click="nextQuestion"
                  :disabled="currentQuestionIndex === quiz.questions.length - 1"
                >
                  Next
                  <i class="bi bi-arrow-right ms-2"></i>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Quiz Completed -->
    <div class="row" v-else-if="quizCompleted">
      <div class="col-md-8 mx-auto">
        <div class="card text-center">
          <div class="card-body py-5">
            <i class="bi bi-check-circle-fill text-success fs-1 mb-3"></i>
            <h3 class="mb-3">Quiz Completed!</h3>
            <p class="lead mb-4">Your quiz has been submitted successfully.</p>

            <div v-if="quizResult" class="row g-3 mb-4">
              <div class="col-md-4">
                <div class="card bg-primary text-white">
                  <div class="card-body">
                    <h4>
                      {{ quizResult.total_scored }}/{{
                        quizResult.total_questions
                      }}
                    </h4>
                    <p class="mb-0">Score</p>
                  </div>
                </div>
              </div>

              <div class="col-md-4">
                <div class="card bg-success text-white">
                  <div class="card-body">
                    <h4>{{ quizResult.percentage }}%</h4>
                    <p class="mb-0">Percentage</p>
                  </div>
                </div>
              </div>

              <div class="col-md-4">
                <div class="card bg-info text-white">
                  <div class="card-body">
                    <h4>{{ timeTaken }}</h4>
                    <p class="mb-0">Time Taken</p>
                  </div>
                </div>
              </div>
            </div>

            <div class="d-flex justify-content-center gap-3">
              <router-link to="/dashboard" class="btn btn-primary">
                <i class="bi bi-speedometer2 me-2"></i>
                Back to Dashboard
              </router-link>
              <button class="btn btn-outline-primary" @click="viewResults">
                <i class="bi bi-graph-up me-2"></i>
                View Detailed Results
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Error State -->
    <div class="row" v-else-if="error">
      <div class="col-md-6 mx-auto">
        <div class="card text-center">
          <div class="card-body py-5">
            <i class="bi bi-exclamation-triangle text-warning fs-1 mb-3"></i>
            <h3 class="mb-3">Error Loading Quiz</h3>
            <p class="text-muted mb-4">{{ error }}</p>
            <router-link to="/dashboard" class="btn btn-primary">
              <i class="bi bi-arrow-left me-2"></i>
              Back to Dashboard
            </router-link>
          </div>
        </div>
      </div>
    </div>

    <!-- Submit Confirmation Modal -->
    <div
      class="modal fade"
      :class="{ show: showSubmitConfirm }"
      :style="{ display: showSubmitConfirm ? 'block' : 'none' }"
      tabindex="-1"
    >
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Submit Quiz</h5>
            <button
              type="button"
              class="btn-close"
              @click="showSubmitConfirm = false"
            ></button>
          </div>
          <div class="modal-body">
            <p>Are you sure you want to submit your quiz?</p>
            <p class="text-muted">
              Answered: {{ answeredCount }}/{{
                quiz?.questions.length || 0
              }}
              questions<br />
              Time remaining: {{ formatTime(timeRemaining) }}
            </p>
          </div>
          <div class="modal-footer">
            <button
              type="button"
              class="btn btn-secondary"
              @click="showSubmitConfirm = false"
            >
              Cancel
            </button>
            <button
              type="button"
              class="btn btn-warning"
              @click="submitQuiz"
              :disabled="submitting"
            >
              <span
                v-if="submitting"
                class="spinner-border spinner-border-sm me-2"
              ></span>
              Submit Quiz
            </button>
          </div>
        </div>
      </div>
    </div>
    <div
      v-if="showSubmitConfirm"
      class="modal-backdrop fade show"
      @click="showSubmitConfirm = false"
    ></div>

    <!-- Exit Confirmation Modal -->
    <div
      class="modal fade"
      :class="{ show: showExitConfirm }"
      :style="{ display: showExitConfirm ? 'block' : 'none' }"
      tabindex="-1"
    >
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Exit Quiz</h5>
            <button
              type="button"
              class="btn-close"
              @click="showExitConfirm = false"
            ></button>
          </div>
          <div class="modal-body">
            <p>Are you sure you want to exit the quiz?</p>
            <p class="text-warning">Your progress will be lost!</p>
          </div>
          <div class="modal-footer">
            <button
              type="button"
              class="btn btn-secondary"
              @click="showExitConfirm = false"
            >
              Cancel
            </button>
            <router-link to="/dashboard" class="btn btn-danger"
              >Exit Quiz</router-link
            >
          </div>
        </div>
      </div>
    </div>
    <div
      v-if="showExitConfirm"
      class="modal-backdrop fade show"
      @click="showExitConfirm = false"
    ></div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted, onUnmounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import api from "../services/api";

export default {
  name: "QuizAttempt",
  setup() {
    const route = useRoute();
    const router = useRouter();

    const loading = ref(false);
    const submitting = ref(false);
    const quiz = ref(null);
    const currentQuestionIndex = ref(0);
    const answers = reactive({});
    const timeRemaining = ref(0);
    const startTime = ref(null);
    const timer = ref(null);
    const quizCompleted = ref(false);
    const quizResult = ref(null);
    const error = ref("");
    const showSubmitConfirm = ref(false);
    const showExitConfirm = ref(false);

    const currentQuestion = computed(() => {
      if (!quiz.value || !quiz.value.questions) return null;
      return quiz.value.questions[currentQuestionIndex.value];
    });

    const answeredCount = computed(() => {
      return Object.keys(answers).length;
    });

    const timeTaken = computed(() => {
      if (!startTime.value || !quizResult.value) return "N/A";
      const totalSeconds = Math.floor((Date.now() - startTime.value) / 1000);
      return formatTime(totalSeconds);
    });

    const loadQuiz = async () => {
      loading.value = true;
      error.value = "";

      try {
        const quizId = route.params.id;
        const response = await api.getQuizForAttempt(quizId);
        quiz.value = response;

        // Parse time duration (HH:MM format) to seconds
        const [hours, minutes] = response.time_duration.split(":").map(Number);
        timeRemaining.value = hours * 3600 + minutes * 60;

        startTime.value = Date.now();
        startTimer();
      } catch (err) {
        console.error("Error loading quiz:", err);
        error.value = err.response?.data?.message || "Failed to load quiz";
      } finally {
        loading.value = false;
      }
    };

    const startTimer = () => {
      timer.value = setInterval(() => {
        timeRemaining.value--;

        if (timeRemaining.value <= 0) {
          // Auto-submit when time runs out
          submitQuiz();
        }
      }, 1000);
    };

    const stopTimer = () => {
      if (timer.value) {
        clearInterval(timer.value);
        timer.value = null;
      }
    };

    const formatTime = (seconds) => {
      const hours = Math.floor(seconds / 3600);
      const minutes = Math.floor((seconds % 3600) / 60);
      const secs = seconds % 60;

      if (hours > 0) {
        return `${hours.toString().padStart(2, "0")}:${minutes
          .toString()
          .padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
      }
      return `${minutes.toString().padStart(2, "0")}:${secs
        .toString()
        .padStart(2, "0")}`;
    };

    const goToQuestion = (index) => {
      if (index >= 0 && index < quiz.value.questions.length) {
        currentQuestionIndex.value = index;
      }
    };

    const nextQuestion = () => {
      if (currentQuestionIndex.value < quiz.value.questions.length - 1) {
        currentQuestionIndex.value++;
      }
    };

    const previousQuestion = () => {
      if (currentQuestionIndex.value > 0) {
        currentQuestionIndex.value--;
      }
    };

    const getQuestionButtonClass = (index) => {
      const question = quiz.value.questions[index];
      const isAnswered = answers[question.id] !== undefined;
      const isCurrent = index === currentQuestionIndex.value;

      if (isCurrent) {
        return isAnswered ? "btn-success" : "btn-primary";
      }
      return isAnswered ? "btn-outline-success" : "btn-outline-secondary";
    };

    const submitQuiz = async () => {
      submitting.value = true;
      stopTimer();

      try {
        // Calculate time taken
        const timeTakenSeconds = Math.floor(
          (Date.now() - startTime.value) / 1000
        );
        const timeTakenFormatted = formatTime(timeTakenSeconds);

        // Prepare submission data
        const submissionData = {
          quiz_id: parseInt(route.params.id),
          answers: answers,
          time_taken: timeTakenFormatted,
        };

        const response = await api.submitQuizScore(submissionData);
        quizResult.value = response;
        quizCompleted.value = true;
        showSubmitConfirm.value = false;
      } catch (err) {
        console.error("Error submitting quiz:", err);
        alert("Failed to submit quiz. Please try again.");
        // Restart timer if submission failed
        if (timeRemaining.value > 0) {
          startTimer();
        }
      } finally {
        submitting.value = false;
      }
    };

    const viewResults = () => {
      // Navigate to detailed results page (to be implemented)
      router.push("/dashboard");
    };

    // Prevent page refresh/navigation during quiz
    const handleBeforeUnload = (event) => {
      if (!quizCompleted.value) {
        event.preventDefault();
        event.returnValue = "";
      }
    };

    onMounted(() => {
      loadQuiz();
      window.addEventListener("beforeunload", handleBeforeUnload);
    });

    onUnmounted(() => {
      stopTimer();
      window.removeEventListener("beforeunload", handleBeforeUnload);
    });

    return {
      loading,
      submitting,
      quiz,
      currentQuestionIndex,
      currentQuestion,
      answers,
      answeredCount,
      timeRemaining,
      timeTaken,
      quizCompleted,
      quizResult,
      error,
      showSubmitConfirm,
      showExitConfirm,
      formatTime,
      goToQuestion,
      nextQuestion,
      previousQuestion,
      getQuestionButtonClass,
      submitQuiz,
      viewResults,
    };
  },
};
</script>
