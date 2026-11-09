<template>
  <div class="checkout-wrapper">
    <!-- Navbar simples -->
    <header class="checkout-nav">
      <div class="nav-brand">{{ publicConfig.brandName || 'ORACLE JURÍDICO' }}</div>
      <div class="user-chip" v-if="user">
        <img v-if="user.picture" :src="user.picture" class="user-avatar" alt="User avatar" />
        <span class="user-email">{{ user.email }}</span>
        <button class="logout-btn" @click="handleLogout">Sair</button>
      </div>
    </header>

    <main class="checkout-content">
      <div class="plan-card">
        <div class="plan-badge">Acesso Profissional</div>
        <h2 class="plan-title">{{ planTitle }}</h2>
        <p class="plan-subtitle">
          Inteligência preditiva com enxame de agentes de IA para escritórios e departamentos jurídicos.
        </p>

        <div class="price-container">
          <span class="currency">R$</span>
          <span class="price-value">{{ planPrice }}</span>
          <span class="period">/ano</span>
        </div>

        <div class="features-list">
          <div class="feature-item">
            <span class="check-icon">✓</span>
            <span>Simulação massiva de cenários judiciais e recursos</span>
          </div>
          <div class="feature-item">
            <span class="check-icon">✓</span>
            <span>Previsão de comportamento de tribunais e colegiados</span>
          </div>
          <div class="feature-item">
            <span class="check-icon">✓</span>
            <span>Enxame com mais de 100 agentes simultâneos (Twitter & Reddit)</span>
          </div>
          <div class="feature-item">
            <span class="check-icon">✓</span>
            <span>Relatórios preditivos estruturados com exportação em PDF</span>
          </div>
          <div class="feature-item">
            <span class="check-icon">✓</span>
            <span>Entrevistas ReACT interativas em tempo real com os agentes</span>
          </div>
          <div class="feature-item">
            <span class="check-icon">✓</span>
            <span>Suporte prioritário e atualizações contínuas</span>
          </div>
        </div>

        <div v-if="errorMsg" class="error-box">
          {{ errorMsg }}
        </div>

        <div v-if="isCheckingStatus" class="status-box">
          <span class="spinner"></span> Verificando aprovação do pagamento...
        </div>

        <button 
          class="checkout-action-btn" 
          :disabled="loading"
          @click="initiatePayment"
        >
          <span v-if="loading" class="spinner"></span>
          <span v-else>Pagar com Mercado Pago (Pix / Cartão) ➔</span>
        </button>

        <div class="security-badges">
          <span class="lock-icon">🔒</span> Pagamento 100% seguro via Mercado Pago. Liberação imediata no Pix e Cartão.
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuth } from '../store/auth'
import { createMercadoPagoPreference, getPaymentStatus } from '../api/auth'

const router = useRouter()
const route = useRoute()
const { state, logout, initAuth } = useAuth()

const loading = ref(false)
const isCheckingStatus = ref(false)
const errorMsg = ref('')

const user = computed(() => state.user)
const publicConfig = computed(() => state.publicConfig.homepage_config || {})
const planTitle = computed(() => state.publicConfig.mp_plan_title || 'Assinatura Anual Oracle Jurídico')
const planPrice = computed(() => state.publicConfig.mp_plan_price || '197,00')

const initiatePayment = async () => {
  loading.value = true
  errorMsg.value = ''

  try {
    const res = await createMercadoPagoPreference()
    if (res && res.success && res.init_point) {
      window.location.href = res.init_point
    } else {
      errorMsg.value = res.error || 'Não foi possível gerar o link de pagamento. Tente novamente mais tarde.'
    }
  } catch (err) {
    errorMsg.value = err.message || 'Erro ao comunicar com o servidor de pagamento.'
  } finally {
    loading.value = false
  }
}

const checkPaymentStatus = async () => {
  isCheckingStatus.value = true
  try {
    const res = await getPaymentStatus()
    if (res && res.success && res.status === 'active') {
      await initAuth()
      router.push('/')
      return
    }
  } catch (e) {
    console.error(e)
  } finally {
    isCheckingStatus.value = false
  }
}

const handleLogout = async () => {
  await logout()
  router.push('/login')
}

onMounted(async () => {
  // If payment return param present
  if (route.query.payment === 'success') {
    await checkPaymentStatus()
    // Poll twice more with delay
    setTimeout(checkPaymentStatus, 3000)
    setTimeout(checkPaymentStatus, 8000)
  }

  // If already active or admin
  if (user.value && (user.value.role === 'admin' || user.value.status === 'active')) {
    router.push('/')
  }
})
</script>

<style scoped>
.checkout-wrapper {
  min-height: 100vh;
  background: radial-gradient(circle at 50% 10%, #151722 0%, #090a0d 100%);
  color: #fff;
  display: flex;
  flex-direction: column;
}

.checkout-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 40px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(15, 17, 24, 0.6);
  backdrop-filter: blur(12px);
}

.nav-brand {
  font-size: 20px;
  font-weight: 800;
  letter-spacing: 2px;
  color: #fff;
}

.user-chip {
  display: flex;
  align-items: center;
  gap: 12px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 6px 14px;
  border-radius: 999px;
  font-size: 13px;
}

.user-avatar {
  width: 24px;
  height: 24px;
  border-radius: 50%;
}

.user-email {
  color: #cbd5e1;
}

.logout-btn {
  background: none;
  border: none;
  color: #94a3b8;
  cursor: pointer;
  font-size: 12px;
  padding: 2px 6px;
  border-radius: 4px;
  transition: all 0.2s;
}

.logout-btn:hover {
  color: #f87171;
  background: rgba(248, 113, 113, 0.1);
}

.checkout-content {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 24px;
}

.plan-card {
  width: 100%;
  max-width: 540px;
  background: rgba(23, 26, 38, 0.95);
  border: 1px solid rgba(234, 179, 8, 0.3);
  border-radius: 20px;
  padding: 40px;
  box-shadow: 0 30px 80px rgba(0, 0, 0, 0.7), 0 0 50px rgba(234, 179, 8, 0.1);
  text-align: center;
}

.plan-badge {
  display: inline-block;
  padding: 6px 14px;
  background: rgba(234, 179, 8, 0.15);
  color: #eab308;
  border: 1px solid rgba(234, 179, 8, 0.4);
  border-radius: 999px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 1.5px;
  text-transform: uppercase;
  margin-bottom: 16px;
}

.plan-title {
  font-size: 26px;
  font-weight: 800;
  margin: 0 0 10px 0;
  color: #ffffff;
}

.plan-subtitle {
  font-size: 14px;
  color: #94a3b8;
  line-height: 1.5;
  margin: 0 0 24px 0;
}

.price-container {
  display: flex;
  align-items: baseline;
  justify-content: center;
  gap: 4px;
  margin-bottom: 28px;
}

.currency {
  font-size: 24px;
  font-weight: 700;
  color: #eab308;
}

.price-value {
  font-size: 52px;
  font-weight: 900;
  color: #fff;
  letter-spacing: -1px;
}

.period {
  font-size: 16px;
  color: #64748b;
}

.features-list {
  text-align: left;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 12px;
  padding: 20px 24px;
  margin-bottom: 28px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 13px;
  color: #cbd5e1;
}

.check-icon {
  color: #10b981;
  font-weight: 900;
  font-size: 15px;
}

.checkout-action-btn {
  width: 100%;
  padding: 16px;
  background: linear-gradient(135deg, #eab308 0%, #ca8a04 100%);
  border: none;
  border-radius: 12px;
  color: #0b0c10;
  font-size: 16px;
  font-weight: 800;
  cursor: pointer;
  transition: all 0.25s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  box-shadow: 0 10px 25px rgba(234, 179, 8, 0.3);
}

.checkout-action-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 14px 30px rgba(234, 179, 8, 0.45);
}

.checkout-action-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.security-badges {
  margin-top: 20px;
  font-size: 12px;
  color: #64748b;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.lock-icon {
  font-size: 14px;
}

.error-box {
  background: rgba(239, 68, 68, 0.15);
  border: 1px solid rgba(239, 68, 68, 0.35);
  color: #fca5a5;
  padding: 12px;
  border-radius: 8px;
  font-size: 13px;
  margin-bottom: 20px;
}

.status-box {
  background: rgba(59, 130, 246, 0.15);
  border: 1px solid rgba(59, 130, 246, 0.35);
  color: #93c5fd;
  padding: 12px;
  border-radius: 8px;
  font-size: 13px;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(0, 0, 0, 0.2);
  border-top-color: #000;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
