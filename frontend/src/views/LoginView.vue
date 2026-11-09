<template>
  <div class="login-wrapper">
    <div class="login-card">
      <div class="brand-header">
        <div class="brand-badge">{{ publicConfig.tagline || 'ORACLE JURÍDICO' }}</div>
        <h1 class="brand-title">{{ publicConfig.brandName || 'ORACLE' }}</h1>
        <p class="brand-subtitle">
          Inteligência Preditiva & Jurimetria com Agentes Autônomos de IA
        </p>
      </div>

      <div class="login-content">
        <div class="info-box">
          <div class="info-title">Acesso à Plataforma</div>
          <div class="info-desc">
            Entre com a sua conta Google para acessar o ambiente de simulações judiciais.
          </div>
        </div>

        <div v-if="errorMsg" class="error-banner">
          {{ errorMsg }}
        </div>

        <div class="google-btn-container">
          <div id="googleSignInButton"></div>
          <div v-if="loading" class="loading-state">
            <span class="spinner"></span> Validando acesso...
          </div>
        </div>

        <div class="terms-text">
          Ao prosseguir, você concorda com os Termos de Serviço e Política de Privacidade do Oracle Jurídico.
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../store/auth'
import { loginWithGoogle } from '../api/auth'

const router = useRouter()
const { state, setAuth } = useAuth()

const loading = ref(false)
const errorMsg = ref('')

const publicConfig = computed(() => state.publicConfig.homepage_config || {})
const googleClientId = computed(() => state.publicConfig.google_client_id || '')

const handleCredentialResponse = async (response) => {
  if (!response || !response.credential) {
    errorMsg.value = 'Falha ao receber credencial do Google.'
    return
  }

  loading.value = true
  errorMsg.value = ''

  try {
    const res = await loginWithGoogle({ credential: response.credential })
    if (res && res.success && res.token && res.user) {
      setAuth(res.token, res.user)

      if (res.user.role === 'admin' || res.user.status === 'active') {
        router.push('/')
      } else {
        router.push('/checkout')
      }
    } else {
      errorMsg.value = res.error || 'Erro ao validar login.'
    }
  } catch (err) {
    errorMsg.value = err.message || 'Erro ao autenticar com o servidor.'
  } finally {
    loading.value = false
  }
}

const renderGoogleButton = () => {
  if (window.google && window.google.accounts) {
    window.google.accounts.id.initialize({
      client_id: googleClientId.value,
      callback: handleCredentialResponse
    })

    const target = document.getElementById('googleSignInButton')
    if (target) {
      target.innerHTML = ''
      window.google.accounts.id.renderButton(target, {
        theme: 'filled_black',
        size: 'large',
        text: 'signin_with',
        shape: 'rectangular',
        width: 320,
        logo_alignment: 'left'
      })
    }
  } else {
    setTimeout(renderGoogleButton, 300)
  }
}

onMounted(() => {
  // If already logged in
  if (state.isAuthenticated && state.user) {
    if (state.user.role === 'admin' || state.user.status === 'active') {
      router.push('/')
    } else {
      router.push('/checkout')
    }
    return
  }

  renderGoogleButton()
})
</script>

<style scoped>
.login-wrapper {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: radial-gradient(circle at 50% 20%, #171822 0%, #0b0c10 100%);
  color: #fff;
  padding: 24px;
}

.login-card {
  width: 100%;
  max-width: 440px;
  background: rgba(22, 24, 34, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 40px 32px;
  box-shadow: 0 24px 60px rgba(0, 0, 0, 0.6), 0 0 40px rgba(234, 179, 8, 0.08);
  backdrop-filter: blur(20px);
}

.brand-header {
  text-align: center;
  margin-bottom: 32px;
}

.brand-badge {
  display: inline-block;
  padding: 4px 12px;
  background: rgba(234, 179, 8, 0.15);
  color: #eab308;
  border: 1px solid rgba(234, 179, 8, 0.3);
  border-radius: 999px;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 1px;
  text-transform: uppercase;
  margin-bottom: 12px;
}

.brand-title {
  font-size: 28px;
  font-weight: 800;
  letter-spacing: 2px;
  margin: 0 0 8px 0;
  background: linear-gradient(135deg, #ffffff 0%, #d1d5db 50%, #9ca3af 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.brand-subtitle {
  font-size: 13px;
  color: #94a3b8;
  line-height: 1.5;
  margin: 0;
}

.info-box {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 10px;
  padding: 16px;
  margin-bottom: 24px;
  text-align: center;
}

.info-title {
  font-size: 14px;
  font-weight: 600;
  color: #f1f5f9;
  margin-bottom: 6px;
}

.info-desc {
  font-size: 12px;
  color: #94a3b8;
  line-height: 1.4;
}

.error-banner {
  background: rgba(239, 68, 68, 0.15);
  border: 1px solid rgba(239, 68, 68, 0.4);
  color: #fca5a5;
  font-size: 13px;
  padding: 12px;
  border-radius: 8px;
  margin-bottom: 20px;
  text-align: center;
}

.google-btn-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  margin-bottom: 24px;
  min-height: 48px;
}

.loading-state {
  margin-top: 12px;
  font-size: 13px;
  color: #eab308;
  display: flex;
  align-items: center;
  gap: 8px;
}

.spinner {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(234, 179, 8, 0.2);
  border-top-color: #eab308;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.terms-text {
  font-size: 11px;
  color: #64748b;
  text-align: center;
  line-height: 1.4;
}
</style>
