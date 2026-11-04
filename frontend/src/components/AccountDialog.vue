<template>
  <div class="overlay" @click.self="$emit('close')">
    <div class="dialog" role="dialog" aria-modal="true" aria-labelledby="account-title">
      <button class="close" :aria-label="$t('help.close')" @click="$emit('close')">×</button>

      <div v-if="view === 'login' || view === 'register'" class="tabs" role="tablist">
        <button
          type="button"
          role="tab"
          :class="{ active: view === 'login' }"
          :aria-selected="view === 'login'"
          @click="go('login')"
        >
          {{ $t('account.login') }}
        </button>
        <button
          type="button"
          role="tab"
          :class="{ active: view === 'register' }"
          :aria-selected="view === 'register'"
          @click="go('register')"
        >
          {{ $t('account.register') }}
        </button>
      </div>

      <!-- logowanie -->
      <form v-if="view === 'login'" class="form" @submit.prevent="submitLogin">
        <h2 id="account-title">{{ $t('account.loginTitle') }}</h2>
        <label class="field">
          <span>{{ $t('account.loginOrEmail') }}</span>
          <input ref="first" v-model.trim="identifier" autocomplete="username" spellcheck="false" />
        </label>
        <label class="field">
          <span>{{ $t('account.password') }}</span>
          <input v-model="password" type="password" autocomplete="current-password" />
        </label>
        <p v-if="error" class="error" role="alert">{{ error }}</p>
        <button type="submit" class="btn btn-gold submit" :disabled="busy || !identifier || !password">
          {{ busy ? $t('account.wait') : $t('account.loginButton') }}
        </button>
        <div class="links">
          <button type="button" class="link-btn" @click="go('reset')">{{ $t('account.forgot') }}</button>
          <button type="button" class="link-btn" @click="go('register')">{{ $t('account.noAccount') }}</button>
        </div>
      </form>

      <!-- rejestracja -->
      <form v-else-if="view === 'register'" class="form" @submit.prevent="submitRegister">
        <h2 id="account-title">{{ $t('account.registerTitle') }}</h2>
        <p class="lead">{{ $t('account.registerLead') }}</p>
        <label class="field">
          <span>{{ $t('account.loginLabel') }}</span>
          <input ref="first" v-model.trim="login" maxlength="20" autocomplete="username" spellcheck="false" />
          <small>{{ $t('account.loginHint') }}</small>
        </label>
        <label class="field">
          <span>{{ $t('account.email') }}</span>
          <input v-model.trim="email" type="email" autocomplete="email" spellcheck="false" />
          <small>{{ $t('account.emailHint') }}</small>
        </label>
        <div class="field-row">
          <label class="field">
            <span>{{ $t('account.password') }}</span>
            <input v-model="password" type="password" autocomplete="new-password" />
          </label>
          <label class="field">
            <span>{{ $t('account.passwordRepeat') }}</span>
            <input v-model="password2" type="password" autocomplete="new-password" />
          </label>
        </div>
        <p v-if="error" class="error" role="alert">{{ error }}</p>
        <button type="submit" class="btn btn-gold submit" :disabled="busy || !login || !email || !password">
          {{ busy ? $t('account.wait') : $t('account.registerButton') }}
        </button>
        <div class="links">
          <button type="button" class="link-btn" @click="go('login')">{{ $t('account.haveAccount') }}</button>
        </div>
      </form>

      <!-- reset hasła: najpierw kod na e-mail, potem nowe hasło -->
      <form v-else-if="!codeSent" class="form" @submit.prevent="submitReset">
        <h2 id="account-title">{{ $t('account.resetTitle') }}</h2>
        <p class="lead">{{ $t('account.resetLead') }}</p>
        <label class="field">
          <span>{{ $t('account.loginOrEmail') }}</span>
          <input ref="first" v-model.trim="identifier" autocomplete="username" spellcheck="false" />
        </label>
        <p v-if="error" class="error" role="alert">{{ error }}</p>
        <button type="submit" class="btn btn-gold submit" :disabled="busy || !identifier">
          {{ busy ? $t('account.wait') : $t('account.sendCode') }}
        </button>
        <div class="links">
          <button type="button" class="link-btn" @click="go('login')">{{ $t('account.backToLogin') }}</button>
        </div>
      </form>

      <form v-else class="form" @submit.prevent="submitCode">
        <h2 id="account-title">{{ $t('account.resetTitle') }}</h2>
        <p class="lead sent">{{ $t('account.codeSent') }}</p>
        <div class="field-row">
          <label class="field code-field">
            <span>{{ $t('account.code') }}</span>
            <input
              ref="code"
              v-model.trim="code"
              inputmode="numeric"
              maxlength="6"
              autocomplete="one-time-code"
              placeholder="000000"
            />
          </label>
          <label class="field">
            <span>{{ $t('account.newPassword') }}</span>
            <input v-model="password" type="password" autocomplete="new-password" />
          </label>
        </div>
        <p v-if="error" class="error" role="alert">{{ error }}</p>
        <button type="submit" class="btn btn-gold submit" :disabled="busy || code.length < 6 || !password">
          {{ busy ? $t('account.wait') : $t('account.setPassword') }}
        </button>
        <div class="links">
          <button type="button" class="link-btn" @click="resend">{{ $t('account.resend') }}</button>
          <button type="button" class="link-btn" @click="go('login')">{{ $t('account.backToLogin') }}</button>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import { account, clearAccountError, confirmReset, logIn, register, requestReset } from '../account'
import { errorText } from '../i18n'

export default {
  name: 'AccountDialog',
  props: {
    // 'login', 'register' albo 'reset'
    mode: {
      type: String,
      default: 'login'
    }
  },
  emits: ['close'],
  data() {
    return {
      view: this.mode,
      identifier: '',
      login: '',
      email: '',
      password: '',
      password2: '',
      code: '',
      localError: ''
    }
  },
  computed: {
    busy() {
      return !!account.pending
    },
    codeSent() {
      return this.view === 'reset' && !!account.resetSentTo
    },
    // błąd z serwera pokazujemy przy formularzu, którego dotyczy
    error() {
      if (this.localError) return this.localError
      const error = account.error
      if (!error) return ''
      const form = this.view === 'reset' ? 'reset' : this.view
      return error.form === form ? errorText(error) : ''
    },
    signedIn() {
      return account.user
    }
  },
  watch: {
    // udane logowanie, rejestracja albo zmiana hasła zamyka okno
    signedIn(user) {
      if (user) this.$emit('close')
    },
    codeSent(sent) {
      if (sent) {
        this.password = ''
        this.$nextTick(() => this.$refs.code && this.$refs.code.focus())
      }
    }
  },
  mounted() {
    clearAccountError()
    account.resetSentTo = ''
    window.addEventListener('keydown', this.onKey)
    this.focusFirst()
  },
  beforeUnmount() {
    window.removeEventListener('keydown', this.onKey)
  },
  methods: {
    go(view) {
      this.view = view
      this.password = ''
      this.password2 = ''
      this.code = ''
      this.localError = ''
      account.resetSentTo = ''
      clearAccountError()
      this.focusFirst()
    },
    focusFirst() {
      this.$nextTick(() => this.$refs.first && this.$refs.first.focus())
    },
    submitLogin() {
      this.localError = ''
      logIn(this.identifier, this.password)
    },
    submitRegister() {
      this.localError = this.password !== this.password2 ? this.$t('account.passwordMismatch') : ''
      if (!this.localError) register(this.login, this.email, this.password)
    },
    submitReset() {
      this.localError = ''
      requestReset(this.identifier)
    },
    submitCode() {
      this.localError = ''
      confirmReset(account.resetSentTo || this.identifier, this.code, this.password)
    },
    resend() {
      this.code = ''
      requestReset(this.identifier)
    },
    onKey(event) {
      if (event.key === 'Escape') this.$emit('close')
    }
  }
}
</script>

<style scoped>
.overlay {
  position: fixed;
  inset: 0;
  z-index: 200;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding: 2rem 1rem;
  overflow-y: auto;
  background: var(--overlay);
}

.dialog {
  position: relative;
  width: min(460px, 100%);
  box-sizing: border-box;
  margin-top: 4vh;
  padding: 1.1rem 1.5rem 1.2rem;
  color: var(--ink);
  background: linear-gradient(180deg, var(--panel-top) 0%, var(--parchment) 60%, var(--parchment-2) 100%);
  border: 1px solid var(--edge);
  border-radius: 14px;
  box-shadow: 0 24px 60px rgba(0, 0, 0, 0.55);
}

.close {
  position: absolute;
  top: 0.6rem;
  right: 0.8rem;
  width: 32px;
  height: 32px;
  font-size: 1.4rem;
  line-height: 1;
  color: var(--ink-soft);
  background: none;
  border: none;
  border-radius: 50%;
  cursor: pointer;
}

.close:hover {
  background: var(--shade);
}

.tabs {
  display: inline-flex;
  margin-bottom: 0.9rem;
  border: 1px solid var(--edge);
  border-radius: 999px;
  overflow: hidden;
}

.tabs button {
  padding: 0.35rem 1rem;
  font: inherit;
  font-size: 0.88rem;
  font-weight: 700;
  color: var(--ink);
  background: var(--card);
  border: none;
  cursor: pointer;
}

.tabs button + button {
  border-left: 1px solid var(--edge);
}

.tabs button.active {
  color: var(--on-accent);
  background: var(--gold);
}

h2 {
  margin: 0 2rem 0.35rem 0;
  font-family: var(--font-title);
  font-size: 1.4rem;
}

.lead {
  margin: 0 0 0.75rem;
  font-size: 0.88rem;
  line-height: 1.4;
  color: var(--ink-soft);
}

.lead.sent {
  padding: 0.5rem 0.7rem;
  color: var(--ink);
  background: var(--glass-2);
  border-left: 3px solid var(--moss);
  border-radius: 6px;
}

.form {
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  min-width: 0;
}

.field > span {
  font-family: var(--font-title);
  font-size: 0.85rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  color: var(--ink-soft);
}

.field small {
  font-size: 0.75rem;
  color: var(--ink-soft);
}

.field input {
  padding: 0.5rem 0.75rem;
  font: inherit;
  font-size: 1rem;
  color: var(--ink);
  background: var(--input-bg);
  border: 1.5px solid var(--edge);
  border-radius: 8px;
}

.field input:focus {
  outline: none;
  border-color: var(--gold);
  box-shadow: 0 0 0 3px rgba(var(--accent-rgb), 0.35);
}

.field-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.65rem;
}

.code-field input {
  font-family: ui-monospace, 'SFMono-Regular', Menlo, Consolas, monospace;
  font-size: 1.15rem;
  letter-spacing: 0.3em;
}

.error {
  margin: 0;
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--blood);
}

.submit {
  align-self: stretch;
  padding: 0.55rem 1rem;
  font-size: 1rem;
}

.links {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 0.4rem 1rem;
}

.link-btn {
  padding: 0;
  font: inherit;
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--gold-dark);
  background: none;
  border: none;
  text-decoration: underline;
  text-underline-offset: 3px;
  cursor: pointer;
}

@media (max-width: 480px) {
  .field-row {
    grid-template-columns: 1fr;
  }
}
</style>
