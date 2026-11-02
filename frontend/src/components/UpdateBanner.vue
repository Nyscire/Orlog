<template>
  <transition name="update-slide">
    <div v-if="visible" class="update-banner" role="status" aria-live="polite">
      <div class="update-icon" aria-hidden="true">↻</div>
      <div class="update-text">
        <strong>{{ title }}</strong>
        <span class="update-sub">{{ subtitle }}</span>
      </div>
      <div class="update-actions">
        <button v-if="state.status === 'ready'" class="btn btn-gold" @click="install">
          {{ state.needsPassword ? $t('update.install') : $t('update.restart') }}
        </button>
        <button v-else class="btn btn-gold" @click="openDownloadPage">{{ $t('update.download') }}</button>
        <button class="btn btn-ghost" @click="dismiss">{{ $t('update.later') }}</button>
      </div>
    </div>
  </transition>
</template>

<script>
// Informacja o nowej wersji aplikacji (tylko w Electronie, zob. electron/updater.cjs).
// Pobieranie idzie po cichu w tle; pasek pojawia się, gdy wersja jest gotowa do instalacji
// albo (przenośny exe) gdy trzeba ją pobrać ze strony z wydaniami.
export default {
  name: 'UpdateBanner',
  data() {
    return {
      state: null,
      dismissed: ''
    }
  },
  computed: {
    visible() {
      const s = this.state
      return !!s && (s.status === 'ready' || s.status === 'available') && this.dismissed !== `${s.status}:${s.version}`
    },
    title() {
      return this.state.status === 'ready'
        ? this.$t('update.readyTitle', { version: this.state.version })
        : this.$t('update.availableTitle', { version: this.state.version })
    },
    subtitle() {
      if (this.state.status === 'available') return this.$t('update.availableText')
      return this.state.needsPassword ? this.$t('update.readyTextPassword') : this.$t('update.readyText')
    }
  },
  mounted() {
    const bridge = window.orlog
    if (!bridge || !bridge.onUpdate) return
    bridge.onUpdate(state => { this.state = state })
    bridge.updateState().then(state => {
      if (state && !this.state) this.state = state
    })
  },
  methods: {
    install() {
      window.orlog.installUpdate()
    },
    openDownloadPage() {
      window.orlog.openDownloadPage()
    },
    dismiss() {
      this.dismissed = `${this.state.status}:${this.state.version}`
    }
  }
}
</script>

<style scoped>
.update-banner {
  position: fixed;
  right: 1rem;
  bottom: 1rem;
  z-index: 150;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  max-width: min(600px, calc(100vw - 2rem));
  padding: 0.65rem 0.8rem 0.65rem 0.7rem;
  color: var(--ink);
  background: linear-gradient(180deg, var(--panel-top), var(--parchment));
  border: 1px solid var(--gold);
  border-radius: 12px;
  box-shadow: 0 0 0 2px rgba(var(--accent-rgb), 0.25), 0 12px 30px rgba(0, 0, 0, 0.45);
}

.update-icon {
  flex: 0 0 auto;
  width: 34px;
  height: 34px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  font-weight: 900;
  color: var(--on-accent);
  background: linear-gradient(180deg, var(--gold-bright), var(--gold));
  border-radius: 50%;
}

.update-text {
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
  min-width: 0;
}

.update-text strong {
  font-family: var(--font-title);
  font-size: 0.95rem;
}

.update-sub {
  font-size: 0.8rem;
  line-height: 1.3;
  color: var(--ink-soft);
}

.update-actions {
  flex: 0 0 auto;
  display: flex;
  gap: 0.4rem;
}

.update-actions .btn {
  padding: 0.35rem 0.85rem;
  font-size: 0.82rem;
  white-space: nowrap;
}

.update-slide-enter-active,
.update-slide-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}

.update-slide-enter-from,
.update-slide-leave-to {
  opacity: 0;
  transform: translateY(12px);
}

@media (max-width: 600px) {
  .update-banner {
    left: 0.75rem;
    right: 0.75rem;
    bottom: 0.75rem;
    flex-wrap: wrap;
  }
}
</style>
