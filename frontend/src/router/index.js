import { createRouter, createWebHistory } from 'vue-router'

// Lazy load components for better performance
const Home = () => import('../views/Home.vue')
const Login = () => import('../views/auth/Login.vue')
const Register = () => import('../views/auth/Register.vue')
const Dashboard = () => import('../views/Dashboard.vue')
const Profile = () => import('../views/Profile.vue')
const QuizAttempt = () => import('../views/QuizAttempt.vue')

// Admin components - lazy loaded
const AdminDashboard = () => import('../views/admin/AdminDashboard.vue')
const SubjectManagement = () => import('../views/admin/SubjectManagement.vue')
const ChapterManagement = () => import('../views/admin/ChapterManagement.vue')
const QuizManagement = () => import('../views/admin/QuizManagement.vue')
const QuestionManagement = () => import('../views/admin/QuestionManagement.vue')
const UserManagement = () => import('../views/admin/UserManagement.vue')

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
