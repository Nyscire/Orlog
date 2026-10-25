<template>
  <div class="overlay" @click.self="$emit('close')">
    <div class="dialog" role="dialog" aria-modal="true" aria-labelledby="settings-title">
      <button class="close" :aria-label="$t('help.close')" @click="$emit('close')">×</button>
      <h2 id="settings-title">{{ $t('settings.title') }}</h2>

      <section>
        <h3>{{ $t('settings.language') }}</h3>
        <div class="segmented">
          <button
            v-for="lang in languages"
            :key="lang.id"
            :class="{ active: current.locale === lang.id }"
            :aria-pressed="current.locale === lang.id"
            @click="set('locale', lang.id)"
          >
            {{ lang.label }}
          </button>
        </div>
      </section>

      <section>
        <h3>{{ $t('settings.theme') }}</h3>
        <div class="options themes">
          <button
            v-for="theme in themes"
            :key="theme"
            class="option"
            :class="{ active: current.theme === theme }"
            :aria-pressed="current.theme === theme"
            @click="set('theme', theme)"
          >
            <!-- mały podgląd: tło, panel, akcent i kość w kolorach danego motywu -->
            <span class="swatch" :data-theme="theme">
              <span class="swatch-panel">
                <span class="swatch-die"></span>
                <span class="swatch-accent"></span>
              </span>
            </span>
            <span class="option-name">{{ $t(`settings.themes.${theme}`) }}</span>
          </button>
        </div>
      </section>

      <section>
        <h3>{{ $t('settings.font') }}</h3>
        <div class="options fonts">
          <button
            v-for="font in fonts"
            :key="font"
            class="option"
            :class="{ active: current.font === font }"
            :aria-pressed="current.font === font"
            @click="set('font', font)"
          >
            <span class="font-sample" :data-font="font">
              <span class="sample-title">Orlog</span>
              <span class="sample-body">{{ $t('settings.sample') }}</span>
            </span>
            <span class="option-name">{{ $t(`settings.fonts.${font}`) }}</span>
          </button>
        </div>
      </section>

      <section>
        <h3>{{ $t('settings.size') }}</h3>
        <div class="segmented">
          <button
            v-for="size in sizes"
            :key="size"
            :class="{ active: current.size === size }"
            :aria-pressed="current.size === size"
            @click="set('size', size)"
          >
            {{ $t(`settings.sizes.${size}`) }}
          </button>
        </div>
      </section>

      <div class="actions">
        <button class="btn btn-gold" @click="$emit('close')">{{ $t('settings.done') }}</button>
      </div>
    </div>
  </div>
</template>

<script>
import { FONTS, LANGUAGES, SIZES, THEMES, setSetting, settings } from '../settings'

export default {
  name: 'SettingsDialog',
  emits: ['close'],
  computed: {
    current() {
      return settings
    },
    languages() {
      return LANGUAGES
    },
    themes() {
      return THEMES
    },
    fonts() {
      return FONTS
    },
    sizes() {
      return SIZES
    }
  },
  mounted() {
    window.addEventListener('keydown', this.onKey)
  },
  beforeUnmount() {
    window.removeEventListener('keydown', this.onKey)
  },
  methods: {
    set(key, value) {
      setSetting(key, value)
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
  width: min(620px, 100%);
  box-sizing: border-box;
  padding: 1.4rem 1.6rem 1.2rem;
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
  background: rgba(0, 0, 0, 0.08);
}

h2 {
  margin: 0 2rem 0.75rem 0;
  font-family: var(--font-title);
  font-size: 1.5rem;
}

section + section {
  margin-top: 1rem;
}

h3 {
  margin: 0 0 0.45rem;
  font-family: var(--font-title);
  font-size: 0.95rem;
  color: var(--gold-dark);
}

.segmented {
  display: inline-flex;
  border: 1px solid var(--edge);
  border-radius: 999px;
  overflow: hidden;
}

.segmented button {
  padding: 0.4rem 1rem;
  font: inherit;
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--ink);
  background: var(--card);
  border: none;
  cursor: pointer;
}

.segmented button + button {
  border-left: 1px solid var(--edge);
}

.segmented button.active {
  color: var(--on-accent);
  background: var(--gold);
}

.options {
  display: grid;
  gap: 0.6rem;
}

.themes {
  grid-template-columns: repeat(auto-fill, minmax(125px, 1fr));
}

.fonts {
  grid-template-columns: repeat(auto-fill, minmax(165px, 1fr));
}

.option {
  display: flex;
  flex-direction: column;
  align-items: stretch;
  gap: 0.4rem;
  padding: 0.5rem;
  font: inherit;
  color: var(--ink);
  text-align: center;
  background: var(--card);
  border: 1.5px solid var(--parchment-3);
  border-radius: 10px;
  cursor: pointer;
}

.option:hover {
  border-color: var(--edge);
}

.option.active {
  border-color: var(--gold);
  box-shadow: 0 0 0 2px rgba(var(--accent-rgb), 0.45);
}

.option-name {
  font-size: 0.85rem;
  font-weight: 600;
}

.swatch {
  display: block;
  height: 54px;
  padding: 8px;
  box-sizing: border-box;
  border-radius: 7px;
  background: var(--wood-800);
}

.swatch-panel {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 100%;
  padding: 0 8px;
  box-sizing: border-box;
  border-radius: 5px;
  background: var(--parchment);
  border: 1px solid var(--edge);
}

.swatch-die {
  width: 20px;
  height: 20px;
  border-radius: 4px;
  background: linear-gradient(145deg, var(--die-1), var(--die-3));
  border: 2px solid var(--gold);
}

.swatch-accent {
  width: 34px;
  height: 12px;
  border-radius: 999px;
  background: linear-gradient(180deg, var(--gold-bright), var(--gold));
}

.font-sample {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
  padding: 0.4rem 0.25rem;
  border-radius: 7px;
  background: rgba(0, 0, 0, 0.04);
}

.sample-title {
  font-family: var(--font-title);
  font-weight: 700;
  font-size: 1.3rem;
  line-height: 1.1;
}

.sample-body {
  font-family: var(--font-body);
  font-size: 0.8rem;
  color: var(--ink-soft);
}

.actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 1.2rem;
}

@media (max-width: 600px) {
  .dialog {
    padding: 1.1rem;
  }
}
</style>
