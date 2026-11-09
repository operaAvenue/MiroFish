import { reactive, computed } from 'vue'
import { getMe, getPublicConfig, logoutUser } from '../api/auth'

const state = reactive({
  user: null,
  token: localStorage.getItem('oracle_token') || null,
  isAuthenticated: false,
  isLoading: true,
  publicConfig: {
    google_client_id: '',
    homepage_config: {
      brandName: 'ORACLE JURÍDICO',
      tagline: 'Inteligência Preditiva & Jurimetria de Enxame',
      version: 'v2.0 Legal Edition',
      heroTitle1: 'Simulação de Cenários Judiciais',
      heroTitle2: 'com Agentes Jurídicos de IA',
      heroDesc: 'Antecipe decisões de tribunais, tendências de votos e repercussões jurídicas através de simulações com enxames massivos de agentes autônomos especializados.',
      slogan: 'A certeza jurídica antes de protocolar sua ação.',
      heroImageUrl: '',
      logoUrl: ''
    },
    mp_public_key: '',
    mp_plan_title: 'Assinatura Anual Oracle Jurídico',
    mp_plan_price: '197.00',
    mp_plan_currency: 'BRL'
  }
})

export function setAuth(token, user) {
  state.token = token
  state.user = user
  state.isAuthenticated = true
  localStorage.setItem('oracle_token', token)
  if (user) {
    localStorage.setItem('oracle_user', JSON.stringify(user))
  }
}

export function clearAuth() {
  state.token = null
  state.user = null
  state.isAuthenticated = false
  localStorage.removeItem('oracle_token')
  localStorage.removeItem('oracle_user')
}

export async function fetchPublicConfig() {
  try {
    const res = await getPublicConfig()
    if (res && res.success && res.data) {
      state.publicConfig = {
        ...state.publicConfig,
        ...res.data,
        homepage_config: {
          ...state.publicConfig.homepage_config,
          ...(res.data.homepage_config || {})
        }
      }
    }
  } catch (err) {
    console.warn('Failed to load public config:', err)
  }
}

export async function initAuth() {
  state.isLoading = true
  await fetchPublicConfig()

  const token = localStorage.getItem('oracle_token')
  if (!token) {
    state.isLoading = false
    return false
  }

  try {
    const res = await getMe()
    if (res && res.success && res.authenticated && res.user) {
      state.user = res.user
      state.token = token
      state.isAuthenticated = true
      localStorage.setItem('oracle_user', JSON.stringify(res.user))
      state.isLoading = false
      return true
    } else {
      clearAuth()
      state.isLoading = false
      return false
    }
  } catch (err) {
    console.warn('Session verification failed:', err)
    clearAuth()
    state.isLoading = false
    return false
  }
}

export async function logout() {
  try {
    await logoutUser()
  } catch (e) {
    console.error(e)
  }
  clearAuth()
}

export const useAuth = () => {
  const isAdmin = computed(() => state.user?.role === 'admin')
  const hasAccess = computed(() => {
    if (!state.user) return false
    if (state.user.role === 'admin') return true
    return state.user.status === 'active'
  })

  return {
    state,
    isAdmin,
    hasAccess,
    setAuth,
    clearAuth,
    initAuth,
    fetchPublicConfig,
    logout
  }
}

export default state
