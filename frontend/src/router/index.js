import { createRouter, createWebHistory } from 'vue-router'

// Import components
import Home from '../views/Home.vue'
import Login from '../views/auth/Login.vue'
import Register from '../views/auth/Register.vue'
import Dashboard from '../views/Dashboard.vue'
import Profile from '../views/Profile.vue'
import QuizAttempt from '../views/QuizAttempt.vue'

// Admin components
import AdminDashboard from '../views/admin/AdminDashboard.vue'
import SubjectManagement from '../views/admin/SubjectManagement.vue'
import ChapterManagement from '../views/admin/ChapterManagement.vue'
import QuizManagement from '../views/admin/QuizManagement.vue'
import QuestionManagement from '../views/admin/QuestionManagement.vue'
import UserManagement from '../views/admin/UserManagement.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresGuest: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: Register,
    meta: { requiresGuest: true }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: Dashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: Profile,
    meta: { requiresAuth: true }
  },
  {
    path: '/quiz/:id/attempt',
    name: 'QuizAttempt',
    component: QuizAttempt,
    meta: { requiresAuth: true, requiresUser: true }
  },
  {
    path: '/admin',
    name: 'AdminDashboard',
    component: AdminDashboard,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/subjects',
    name: 'SubjectManagement',
    component: SubjectManagement,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/chapters',
    name: 'ChapterManagement',
    component: ChapterManagement,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/quizzes',
    name: 'QuizManagement',
    component: QuizManagement,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/questions',
    name: 'QuestionManagement',
    component: QuestionManagement,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/users',
    name: 'UserManagement',
    component: UserManagement,
    meta: { requiresAuth: true, requiresAdmin: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guards
router.beforeEach((to, from, next) => {
  const isAuthenticated = !!localStorage.getItem('access_token')
  const user = JSON.parse(localStorage.getItem('user') || '{}')
  const isAdmin = user.is_admin || false

  if (to.meta.requiresGuest && isAuthenticated) {
    next('/dashboard')
  } else if (to.meta.requiresAuth && !isAuthenticated) {
    next('/login')
  } else if (to.meta.requiresAdmin && !isAdmin) {
    next('/dashboard')
  } else if (to.meta.requiresUser && isAdmin) {
    next('/admin')
  } else {
    next()
  }
})

export default router
