import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Process from '../views/MainView.vue'
import SimulationView from '../views/SimulationView.vue'
import SimulationRunView from '../views/SimulationRunView.vue'
import ReportView from '../views/ReportView.vue'
import InteractionView from '../views/InteractionView.vue'
import LoginView from '../views/LoginView.vue'
import CheckoutView from '../views/CheckoutView.vue'
import AdminView from '../views/AdminView.vue'
import { useAuth } from '../store/auth'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: LoginView
  },
  {
    path: '/checkout',
    name: 'Checkout',
    component: CheckoutView
  },
  {
    path: '/admin',
    name: 'Admin',
    component: AdminView
  },
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/process/:projectId',
    name: 'Process',
    component: Process,
    props: true
  },
  {
    path: '/simulation/:simulationId',
    name: 'Simulation',
    component: SimulationView,
    props: true
  },
  {
    path: '/simulation/:simulationId/start',
    name: 'SimulationRun',
    component: SimulationRunView,
    props: true
  },
  {
    path: '/report/:reportId',
    name: 'Report',
    component: ReportView,
    props: true
  },
  {
    path: '/interaction/:reportId',
    name: 'Interaction',
    component: InteractionView,
    props: true
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach(async (to, from, next) => {
  const { state, initAuth } = useAuth()

  if (state.isLoading) {
    await initAuth()
  }

  // Public login page
  if (to.path === '/login') {
    if (state.isAuthenticated && state.user) {
      if (state.user.role === 'admin' || state.user.status === 'active') {
        return next('/')
      } else {
        return next('/checkout')
      }
    }
    return next()
  }

  // If not logged in -> redirect to /login
  if (!state.isAuthenticated || !state.user) {
    return next('/login')
  }

  // Check admin route
  if (to.path === '/admin') {
    if (state.user.role === 'admin') {
      return next()
    } else {
      return next('/')
    }
  }

  // Check paywall status for non-admin users
  if (state.user.role !== 'admin' && state.user.status !== 'active') {
    if (to.path !== '/checkout') {
      return next('/checkout')
    }
    return next()
  }

  // If active user tries to visit checkout
  if (to.path === '/checkout' && (state.user.role === 'admin' || state.user.status === 'active')) {
    return next('/')
  }

  next()
})

export default router
