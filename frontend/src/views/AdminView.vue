<template>
  <div class="admin-wrapper">
    <!-- Header -->
    <header class="admin-header">
      <div class="header-left">
        <router-link to="/" class="back-link">← Voltar ao App</router-link>
        <h1 class="header-title">Painel Administrativo Oracle</h1>
      </div>
      <div class="header-right">
        <span class="admin-badge">Super Admin: {{ user?.email }}</span>
        <button class="logout-btn" @click="handleLogout">Sair</button>
      </div>
    </header>

    <!-- Nav Tabs -->
    <div class="tabs-nav">
      <button 
        class="tab-btn" 
        :class="{ active: currentTab === 'users' }" 
        @click="currentTab = 'users'"
      >
        👥 Gestão de Usuários ({{ users.length }})
      </button>
      <button 
        class="tab-btn" 
        :class="{ active: currentTab === 'pagebuilder' }" 
        @click="currentTab = 'pagebuilder'"
      >
        🎨 PageBuilder (Página Inicial)
      </button>
      <button 
        class="tab-btn" 
        :class="{ active: currentTab === 'settings' }" 
        @click="currentTab = 'settings'"
      >
        ⚙️ Mercado Pago & Credenciais
      </button>
    </div>

    <!-- Feedback Message -->
    <div v-if="toastMsg" class="toast-banner" :class="toastType">
      {{ toastMsg }}
    </div>

    <!-- Main Content -->
    <main class="admin-body">
      <!-- ABA 1: USUÁRIOS -->
      <section v-if="currentTab === 'users'" class="tab-pane">
        <div class="pane-header">
          <div>
            <h2 class="pane-title">Controle de Usuários & Acessos</h2>
            <p class="pane-subtitle">Gerencie os usuários cadastrados via Google OAuth e conceda acesso manualmente.</p>
          </div>
          <div class="search-box">
            <input 
              v-model="userSearch" 
              type="text" 
              placeholder="Buscar por e-mail ou nome..." 
              class="admin-input search-input" 
            />
          </div>
        </div>

        <div class="table-container">
          <table class="admin-table">
            <thead>
              <tr>
                <th>Usuário</th>
                <th>E-mail</th>
                <th>Perfil</th>
                <th>Status de Acesso</th>
                <th>Criado em</th>
                <th>Ações</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="u in filteredUsers" :key="u.id">
                <td>
                  <div class="user-cell">
                    <img v-if="u.picture" :src="u.picture" class="table-avatar" alt="User avatar" />
                    <div v-else class="table-avatar-placeholder">{{ u.name ? u.name[0] : 'U' }}</div>
                    <span class="user-cell-name">{{ u.name || 'Sem nome' }}</span>
                  </div>
                </td>
                <td class="email-cell">{{ u.email }}</td>
                <td>
                  <span class="role-badge" :class="u.role">{{ u.role === 'admin' ? 'Administrador' : 'Cliente' }}</span>
                </td>
                <td>
                  <select 
                    v-model="u.status" 
                    class="status-select" 
                    :class="u.status"
                    @change="onUserStatusChange(u)"
                  >
                    <option value="active">🟢 Ativo (Acesso Liberado)</option>
                    <option value="pending_payment">🟡 Pendente Pagamento</option>
                    <option value="blocked">🔴 Bloqueado</option>
                  </select>
                </td>
                <td class="date-cell">{{ formatDate(u.created_at) }}</td>
                <td>
                  <div class="actions-cell">
                    <button 
                      v-if="u.role !== 'admin'" 
                      class="btn-text green" 
                      @click="quickActivate(u)"
                      title="Liberar Acesso Imediatamente"
                    >
                      Liberar Acesso
                    </button>
                    <button 
                      v-if="u.email !== user?.email" 
                      class="btn-text red" 
                      @click="onDeleteUser(u)"
                      title="Excluir Usuário"
                    >
                      Excluir
                    </button>
                  </div>
                </td>
              </tr>
              <tr v-if="filteredUsers.length === 0">
                <td colspan="6" class="empty-cell">Nenhum usuário encontrado.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <!-- ABA 2: PAGEBUILDER -->
      <section v-if="currentTab === 'pagebuilder'" class="tab-pane">
        <div class="pane-header">
          <div>
            <h2 class="pane-title">PageBuilder da Página Inicial</h2>
            <p class="pane-subtitle">Altere textos, títulos, logotipo e imagem de destaque da tela inicial em tempo real.</p>
          </div>
          <button class="save-btn" :disabled="saving" @click="savePageBuilder">
            {{ saving ? 'Salvando...' : 'Salvar Alterações' }}
          </button>
        </div>

        <div class="pagebuilder-grid">
          <!-- Formulário de Edição -->
          <div class="builder-form">
            <h3 class="section-title">Textos Principais</h3>

            <div class="form-group">
              <label class="form-label">Nome da Marca (Navbar / Logo)</label>
              <input v-model="pageConfig.brandName" type="text" class="admin-input" placeholder="ex: ORACLE JURÍDICO" />
            </div>

            <div class="form-row">
              <div class="form-group flex-1">
                <label class="form-label">Tagline / Badge Laranja</label>
                <input v-model="pageConfig.tagline" type="text" class="admin-input" placeholder="ex: Inteligência Preditiva & Jurimetria" />
              </div>
              <div class="form-group flex-1">
                <label class="form-label">Versão</label>
                <input v-model="pageConfig.version" type="text" class="admin-input" placeholder="ex: v2.0 Legal Edition" />
              </div>
            </div>

            <div class="form-group">
              <label class="form-label">Título Linha 1</label>
              <input v-model="pageConfig.heroTitle1" type="text" class="admin-input" placeholder="ex: Simulação de Cenários Judiciais" />
            </div>

            <div class="form-group">
              <label class="form-label">Título Linha 2 (Destaque Gradiente)</label>
              <input v-model="pageConfig.heroTitle2" type="text" class="admin-input" placeholder="ex: com Agentes Jurídicos de IA" />
            </div>

            <div class="form-group">
              <label class="form-label">Descrição do Hero</label>
              <textarea v-model="pageConfig.heroDesc" rows="4" class="admin-textarea" placeholder="Descreva a proposta de valor do produto jurídico..."></textarea>
            </div>

            <div class="form-group">
              <label class="form-label">Slogan (com cursor terminal)</label>
              <input v-model="pageConfig.slogan" type="text" class="admin-input" placeholder="ex: A certeza jurídica antes de protocolar sua ação." />
            </div>

            <h3 class="section-title" style="margin-top: 24px;">Imagens & Logotipo</h3>

            <div class="form-group">
              <label class="form-label">Logotipo (URL ou Upload)</label>
              <div class="file-upload-row">
                <input v-model="pageConfig.logoUrl" type="text" class="admin-input flex-1" placeholder="URL da imagem do logo..." />
                <label class="upload-file-btn">
                  <span>Subir Arquivo</span>
                  <input type="file" accept="image/*" class="hidden-file-input" @change="e => uploadAssetFile(e, 'logoUrl')" />
                </label>
              </div>
            </div>

            <div class="form-group">
              <label class="form-label">Imagem de Destaque do Hero (URL ou Upload)</label>
              <div class="file-upload-row">
                <input v-model="pageConfig.heroImageUrl" type="text" class="admin-input flex-1" placeholder="URL da imagem da hero section..." />
                <label class="upload-file-btn">
                  <span>Subir Arquivo</span>
                  <input type="file" accept="image/*" class="hidden-file-input" @change="e => uploadAssetFile(e, 'heroImageUrl')" />
                </label>
              </div>
            </div>

            <div class="form-actions-row">
              <button class="save-btn" :disabled="saving" @click="savePageBuilder">
                {{ saving ? 'Salvando...' : 'Salvar Alterações' }}
              </button>
              <button class="reset-btn" @click="resetPageBuilderDefaults">
                Restaurar Padrão
              </button>
            </div>
          </div>

          <!-- Preview da Hero Section -->
          <div class="builder-preview">
            <h3 class="section-title">Prévia da Página Inicial</h3>
            <div class="hero-preview-box">
              <div class="preview-navbar">
                <span class="preview-brand">{{ pageConfig.brandName || 'ORACLE JURÍDICO' }}</span>
                <span class="preview-link">Visitar Github ↗</span>
              </div>
              <div class="preview-hero-body">
                <div class="preview-left">
                  <div class="preview-tags">
                    <span class="preview-tag-badge">{{ pageConfig.tagline || 'TAGLINE' }}</span>
                    <span class="preview-version">{{ pageConfig.version || 'v2.0' }}</span>
                  </div>
                  <h2 class="preview-title">
                    {{ pageConfig.heroTitle1 || 'Título Linha 1' }}<br>
                    <span class="preview-gradient">{{ pageConfig.heroTitle2 || 'Título Linha 2' }}</span>
                  </h2>
                  <p class="preview-desc">{{ pageConfig.heroDesc || 'Descrição do produto...' }}</p>
                  <p class="preview-slogan">{{ pageConfig.slogan || 'Slogan...' }}<span class="cursor">_</span></p>
                </div>
                <div class="preview-right">
                  <img 
                    v-if="pageConfig.heroImageUrl" 
                    :src="pageConfig.heroImageUrl" 
                    class="preview-hero-img" 
                    alt="Preview" 
                  />
                  <div v-else class="preview-placeholder">
                    <span>Área da Imagem do Hero</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- ABA 3: MERCADO PAGO & CREDENCIAIS -->
      <section v-if="currentTab === 'settings'" class="tab-pane">
        <div class="pane-header">
          <div>
            <h2 class="pane-title">Configurações de Pagamento & Integrações</h2>
            <p class="pane-subtitle">Cadastre as credenciais do Mercado Pago e autenticação Google.</p>
          </div>
          <button class="save-btn" :disabled="saving" @click="saveSettings">
            {{ saving ? 'Salvando...' : 'Salvar Configurações' }}
          </button>
        </div>

        <div class="settings-grid">
          <!-- Mercado Pago -->
          <div class="settings-card">
            <h3 class="card-title">Mercado Pago (Checkout & Pagamentos)</h3>
            <p class="card-desc">Gera o link de pagamento Pix/Cartão para liberar o acesso dos novos clientes.</p>

            <div class="form-group">
              <label class="form-label">Access Token (Produção)</label>
              <input 
                v-model="settingsForm.mp_access_token" 
                type="password" 
                class="admin-input" 
                placeholder="APP_USR-..." 
              />
            </div>

            <div class="form-group">
              <label class="form-label">Public Key (Produção)</label>
              <input 
                v-model="settingsForm.mp_public_key" 
                type="text" 
                class="admin-input" 
                placeholder="APP_USR-..." 
              />
            </div>

            <div class="form-row">
              <div class="form-group flex-2">
                <label class="form-label">Título do Plano de Acesso</label>
                <input 
                  v-model="settingsForm.mp_plan_title" 
                  type="text" 
                  class="admin-input" 
                  placeholder="ex: Assinatura Anual Oracle Jurídico" 
                />
              </div>
              <div class="form-group flex-1">
                <label class="form-label">Valor (R$)</label>
                <input 
                  v-model="settingsForm.mp_plan_price" 
                  type="text" 
                  class="admin-input" 
                  placeholder="ex: 197.00" 
                />
              </div>
            </div>

            <div class="webhook-info-box">
              <div class="webhook-label">URL do Webhook Mercado Pago (Notificação IPN):</div>
              <div class="webhook-url-row">
                <code>https://oracle.fcsg.fr/api/payments/mercadopago/webhook</code>
                <button class="copy-btn" @click="copyWebhookUrl">Copiar URL</button>
              </div>
              <p class="webhook-hint">Cole esta URL no painel do Mercado Pago em Notificações Webhook para ativação automática instantânea.</p>
            </div>
          </div>

          <!-- Google OAuth & Admin -->
          <div class="settings-card">
            <h3 class="card-title">Google OAuth 2.0</h3>
            <p class="card-desc">Credenciais utilizadas para login dos usuários.</p>

            <div class="form-group">
              <label class="form-label">E-mail do Administrador Principal</label>
              <input 
                v-model="settingsForm.admin_email" 
                type="email" 
                class="admin-input" 
                placeholder="seu.email@gmail.com" 
              />
            </div>

            <div class="form-group">
              <label class="form-label">Google Client ID</label>
              <input 
                v-model="settingsForm.google_client_id" 
                type="text" 
                class="admin-input" 
              />
            </div>

            <div class="form-group">
              <label class="form-label">Google Client Secret</label>
              <input 
                v-model="settingsForm.google_client_secret" 
                type="password" 
                class="admin-input" 
              />
            </div>

            <div class="webhook-info-box">
              <div class="webhook-label">Origens autorizadas do Google Cloud Console:</div>
              <code style="display:block; margin: 4px 0;">https://oracle.fcsg.fr</code>
              <div class="webhook-label" style="margin-top: 8px;">URIs de redirecionamento autorizadas:</div>
              <code style="display:block; margin: 4px 0;">https://oracle.fcsg.fr</code>
            </div>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../store/auth'
import { 
  getAdminUsers, 
  updateAdminUser, 
  deleteAdminUser, 
  getAdminSettings, 
  updateAdminSettings, 
  uploadAdminAsset 
} from '../api/auth'

const router = useRouter()
const { state, logout, fetchPublicConfig } = useAuth()

const currentTab = ref('users')
const saving = ref(false)
const toastMsg = ref('')
const toastType = ref('success')

const user = computed(() => state.user)

// Users
const users = ref([])
const userSearch = ref('')

// Settings form
const settingsForm = reactive({
  admin_email: 'roger.ra@gmail.com',
  google_client_id: '',
  google_client_secret: '',
  mp_access_token: '',
  mp_public_key: '',
  mp_webhook_secret: '',
  mp_plan_title: 'Assinatura Anual Oracle Jurídico',
  mp_plan_price: '197.00',
  mp_plan_currency: 'BRL'
})

// PageBuilder config
const pageConfig = reactive({
  brandName: 'ORACLE JURÍDICO',
  tagline: 'Inteligência Preditiva & Jurimetria',
  version: 'v2.0 Legal Edition',
  heroTitle1: 'Simulação de Cenários Judiciais',
  heroTitle2: 'com Agentes Jurídicos de IA',
  heroDesc: 'Antecipe decisões de tribunais, tendências de votos e repercussões jurídicas através de simulações com enxames massivos de agentes autônomos especializados.',
  slogan: 'A certeza jurídica antes de protocolar sua ação.',
  heroImageUrl: '',
  logoUrl: ''
})

const showToast = (msg, type = 'success') => {
  toastMsg.value = msg
  toastType.value = type
  setTimeout(() => {
    toastMsg.value = ''
  }, 4000)
}

const formatDate = (isoStr) => {
  if (!isoStr) return '-'
  try {
    const d = new Date(isoStr)
    return d.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' })
  } catch (e) {
    return isoStr
  }
}

const filteredUsers = computed(() => {
  const q = userSearch.value.trim().toLowerCase()
  if (!q) return users.value
  return users.value.filter(u => 
    (u.email && u.email.toLowerCase().includes(q)) || 
    (u.name && u.name.toLowerCase().includes(q))
  )
})

const loadUsers = async () => {
  try {
    const res = await getAdminUsers()
    if (res && res.success && res.data) {
      users.value = res.data
    }
  } catch (e) {
    showToast(e.message || 'Erro ao carregar lista de usuários.', 'error')
  }
}

const loadSettings = async () => {
  try {
    const res = await getAdminSettings()
    if (res && res.success && res.data) {
      const data = res.data
      Object.assign(settingsForm, {
        admin_email: data.admin_email || 'roger.ra@gmail.com',
        google_client_id: data.google_client_id || '',
        google_client_secret: data.google_client_secret || '',
        mp_access_token: data.mp_access_token || '',
        mp_public_key: data.mp_public_key || '',
        mp_webhook_secret: data.mp_webhook_secret || '',
        mp_plan_title: data.mp_plan_title || 'Assinatura Anual Oracle Jurídico',
        mp_plan_price: data.mp_plan_price || '197.00',
        mp_plan_currency: data.mp_plan_currency || 'BRL'
      })

      if (data.homepage_config) {
        Object.assign(pageConfig, data.homepage_config)
      }
    }
  } catch (e) {
    showToast(e.message || 'Erro ao carregar configurações.', 'error')
  }
}

const onUserStatusChange = async (u) => {
  try {
    const res = await updateAdminUser(u.id, { status: u.status })
    if (res && res.success) {
      showToast(`Status do usuário ${u.email} alterado para ${u.status}.`)
    }
  } catch (e) {
    showToast(e.message || 'Erro ao atualizar usuário.', 'error')
  }
}

const quickActivate = async (u) => {
  u.status = 'active'
  await onUserStatusChange(u)
}

const onDeleteUser = async (u) => {
  if (!confirm(`Deseja realmente excluir o usuário ${u.email}?`)) return
  try {
    const res = await deleteAdminUser(u.id)
    if (res && res.success) {
      showToast('Usuário excluído com sucesso.')
      users.value = users.value.filter(item => item.id !== u.id)
    }
  } catch (e) {
    showToast(e.message || 'Erro ao excluir usuário.', 'error')
  }
}

const saveSettings = async () => {
  saving.value = true
  try {
    const res = await updateAdminSettings(settingsForm)
    if (res && res.success) {
      showToast('Configurações do Mercado Pago salvas com sucesso!')
      await fetchPublicConfig()
    }
  } catch (e) {
    showToast(e.message || 'Erro ao salvar configurações.', 'error')
  } finally {
    saving.value = false
  }
}

const savePageBuilder = async () => {
  saving.value = true
  try {
    const res = await updateAdminSettings({
      homepage_config: pageConfig
    })
    if (res && res.success) {
      showToast('Página inicial atualizada com sucesso!')
      await fetchPublicConfig()
    }
  } catch (e) {
    showToast(e.message || 'Erro ao salvar página.', 'error')
  } finally {
    saving.value = false
  }
}

const resetPageBuilderDefaults = () => {
  Object.assign(pageConfig, {
    brandName: 'ORACLE JURÍDICO',
    tagline: 'Inteligência Preditiva & Jurimetria',
    version: 'v2.0 Legal Edition',
    heroTitle1: 'Simulação de Cenários Judiciais',
    heroTitle2: 'com Agentes Jurídicos de IA',
    heroDesc: 'Antecipe decisões de tribunais, tendências de votos e repercussões jurídicas através de simulações com enxames massivos de agentes autônomos especializados.',
    slogan: 'A certeza jurídica antes de protocolar sua ação.',
    heroImageUrl: '',
    logoUrl: ''
  })
}

const uploadAssetFile = async (event, targetField) => {
  const file = event.target.files[0]
  if (!file) return

  try {
    showToast('Enviando arquivo...', 'success')
    const res = await uploadAdminAsset(file)
    if (res && res.success && res.url) {
      pageConfig[targetField] = res.url
      showToast('Upload concluído com sucesso!')
    }
  } catch (e) {
    showToast(e.message || 'Erro no upload do arquivo.', 'error')
  }
}

const copyWebhookUrl = () => {
  navigator.clipboard.writeText('https://oracle.fcsg.fr/api/payments/mercadopago/webhook')
  showToast('URL copiada para a área de transferência!')
}

const handleLogout = async () => {
  await logout()
  router.push('/login')
}

onMounted(async () => {
  if (!state.user || state.user.role !== 'admin') {
    router.push('/')
    return
  }
  await Promise.all([loadUsers(), loadSettings()])
})
</script>

<style scoped>
.admin-wrapper {
  min-height: 100vh;
  background: #0d0e14;
  color: #f1f5f9;
  display: flex;
  flex-direction: column;
}

.admin-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 18px 36px;
  background: rgba(18, 20, 29, 0.9);
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 20px;
}

.back-link {
  color: #94a3b8;
  text-decoration: none;
  font-size: 13px;
  font-weight: 600;
  padding: 6px 12px;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.05);
  transition: all 0.2s;
}

.back-link:hover {
  color: #fff;
  background: rgba(255, 255, 255, 0.1);
}

.header-title {
  font-size: 20px;
  font-weight: 800;
  letter-spacing: 0.5px;
  margin: 0;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.admin-badge {
  font-size: 12px;
  color: #eab308;
  background: rgba(234, 179, 8, 0.1);
  border: 1px solid rgba(234, 179, 8, 0.3);
  padding: 4px 10px;
  border-radius: 999px;
  font-weight: 600;
}

.logout-btn {
  background: none;
  border: 1px solid rgba(248, 113, 113, 0.3);
  color: #f87171;
  padding: 6px 12px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
}

.logout-btn:hover {
  background: rgba(248, 113, 113, 0.15);
}

.tabs-nav {
  display: flex;
  gap: 8px;
  padding: 12px 36px;
  background: rgba(15, 17, 24, 0.6);
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.tab-btn {
  padding: 10px 18px;
  background: transparent;
  border: 1px solid transparent;
  color: #94a3b8;
  font-size: 13px;
  font-weight: 600;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.tab-btn:hover {
  color: #fff;
  background: rgba(255, 255, 255, 0.04);
}

.tab-btn.active {
  color: #eab308;
  background: rgba(234, 179, 8, 0.1);
  border-color: rgba(234, 179, 8, 0.3);
}

.toast-banner {
  margin: 16px 36px 0;
  padding: 12px 18px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
}

.toast-banner.success {
  background: rgba(16, 185, 129, 0.15);
  border: 1px solid rgba(16, 185, 129, 0.4);
  color: #6ee7b7;
}

.toast-banner.error {
  background: rgba(239, 68, 68, 0.15);
  border: 1px solid rgba(239, 68, 68, 0.4);
  color: #fca5a5;
}

.admin-body {
  flex: 1;
  padding: 28px 36px 60px;
}

.pane-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.pane-title {
  font-size: 22px;
  font-weight: 800;
  margin: 0 0 4px;
}

.pane-subtitle {
  font-size: 13px;
  color: #94a3b8;
  margin: 0;
}

.table-container {
  background: rgba(20, 22, 32, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  overflow: hidden;
}

.admin-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.admin-table th {
  background: rgba(255, 255, 255, 0.03);
  padding: 14px 18px;
  text-align: left;
  font-weight: 600;
  color: #94a3b8;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.admin-table td {
  padding: 14px 18px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
}

.user-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}

.table-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
}

.table-avatar-placeholder {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: #3b82f6;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 12px;
}

.role-badge {
  padding: 3px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 700;
}

.role-badge.admin {
  background: rgba(234, 179, 8, 0.15);
  color: #eab308;
}

.role-badge.user {
  background: rgba(148, 163, 184, 0.15);
  color: #94a3b8;
}

.status-select {
  padding: 6px 10px;
  border-radius: 6px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: #141724;
  color: #fff;
  font-size: 12px;
  cursor: pointer;
}

.status-select.active {
  border-color: rgba(16, 185, 129, 0.4);
  color: #34d399;
}

.status-select.pending_payment {
  border-color: rgba(234, 179, 8, 0.4);
  color: #facc15;
}

.status-select.blocked {
  border-color: rgba(239, 68, 68, 0.4);
  color: #f87171;
}

.actions-cell {
  display: flex;
  gap: 12px;
}

.btn-text {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 12px;
  font-weight: 600;
  padding: 0;
}

.btn-text.green {
  color: #10b981;
}

.btn-text.green:hover {
  text-decoration: underline;
}

.btn-text.red {
  color: #ef4444;
}

.btn-text.red:hover {
  text-decoration: underline;
}

/* PageBuilder Layout */
.pagebuilder-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 28px;
}

.builder-form, .settings-card {
  background: rgba(20, 22, 32, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 14px;
  padding: 28px;
}

.settings-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 28px;
}

.section-title, .card-title {
  font-size: 16px;
  font-weight: 700;
  margin: 0 0 16px;
  color: #fff;
}

.card-desc {
  font-size: 12px;
  color: #94a3b8;
  margin: -10px 0 20px;
}

.form-group {
  margin-bottom: 16px;
}

.form-row {
  display: flex;
  gap: 14px;
}

.flex-1 { flex: 1; }
.flex-2 { flex: 2; }

.form-label {
  display: block;
  font-size: 12px;
  font-weight: 600;
  color: #cbd5e1;
  margin-bottom: 6px;
}

.admin-input, .admin-textarea {
  width: 100%;
  padding: 10px 14px;
  background: #0f111a;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  color: #fff;
  font-size: 13px;
  box-sizing: border-box;
}

.admin-input:focus, .admin-textarea:focus {
  border-color: #eab308;
  outline: none;
}

.file-upload-row {
  display: flex;
  gap: 10px;
}

.upload-file-btn {
  padding: 10px 16px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 8px;
  font-size: 12px;
  font-weight: 600;
  color: #cbd5e1;
  cursor: pointer;
  white-space: nowrap;
  display: flex;
  align-items: center;
}

.upload-file-btn:hover {
  background: rgba(255, 255, 255, 0.15);
  color: #fff;
}

.hidden-file-input {
  display: none;
}

.form-actions-row {
  display: flex;
  gap: 12px;
  margin-top: 24px;
}

.save-btn {
  padding: 10px 22px;
  background: #eab308;
  color: #0b0c10;
  border: none;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
}

.save-btn:hover:not(:disabled) {
  background: #facc15;
}

.reset-btn {
  padding: 10px 18px;
  background: transparent;
  color: #94a3b8;
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 8px;
  font-size: 13px;
  cursor: pointer;
}

.reset-btn:hover {
  color: #fff;
  border-color: rgba(255, 255, 255, 0.3);
}

.hero-preview-box {
  background: #090a0f;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 24px;
}

.preview-navbar {
  display: flex;
  justify-content: space-between;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  padding-bottom: 12px;
  margin-bottom: 20px;
}

.preview-brand {
  font-weight: 800;
  font-size: 14px;
  color: #fff;
  letter-spacing: 1px;
}

.preview-link {
  font-size: 11px;
  color: #94a3b8;
}

.preview-hero-body {
  display: grid;
  grid-template-columns: 1.2fr 0.8fr;
  gap: 16px;
}

.preview-tag-badge {
  background: rgba(234, 179, 8, 0.15);
  color: #eab308;
  font-size: 9px;
  font-weight: 700;
  padding: 2px 6px;
  border-radius: 4px;
  margin-right: 6px;
}

.preview-version {
  font-size: 9px;
  color: #64748b;
}

.preview-title {
  font-size: 18px;
  font-weight: 800;
  line-height: 1.2;
  margin: 10px 0 8px;
}

.preview-gradient {
  background: linear-gradient(135deg, #eab308 0%, #f97316 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.preview-desc {
  font-size: 11px;
  color: #94a3b8;
  line-height: 1.4;
  margin: 0 0 10px;
}

.preview-slogan {
  font-size: 11px;
  color: #f1f5f9;
  font-family: monospace;
}

.cursor {
  animation: blink 1s infinite;
}

@keyframes blink {
  50% { opacity: 0; }
}

.preview-hero-img {
  width: 100%;
  border-radius: 8px;
  object-fit: cover;
}

.preview-placeholder {
  height: 120px;
  border: 1px dashed rgba(255, 255, 255, 0.15);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  color: #64748b;
}

.webhook-info-box {
  margin-top: 18px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 8px;
  padding: 14px;
}

.webhook-label {
  font-size: 11px;
  color: #cbd5e1;
  font-weight: 600;
  margin-bottom: 6px;
}

.webhook-url-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  background: #0b0c10;
  padding: 8px 12px;
  border-radius: 6px;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.webhook-url-row code {
  font-size: 11px;
  color: #eab308;
  word-break: break-all;
}

.copy-btn {
  background: rgba(234, 179, 8, 0.15);
  color: #eab308;
  border: 1px solid rgba(234, 179, 8, 0.3);
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 11px;
  cursor: pointer;
  white-space: nowrap;
}

.copy-btn:hover {
  background: rgba(234, 179, 8, 0.25);
}

.webhook-hint {
  font-size: 11px;
  color: #64748b;
  margin: 8px 0 0;
}
</style>
