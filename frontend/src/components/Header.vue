<script setup lang="ts">
defineProps<{ activeLink?: string }>()

const navItems = [
  { label: 'Phim nổi bật', href: '#movies' },
  { label: 'AI Discovery', href: '#ai' },
  { label: 'Showtimes', href: '#showtimes' },
  { label: 'Theaters', href: '#theaters' },
]
</script>

<template>
  <nav class="topbar">
    <div class="topbar__brand-wrap">
      <a class="brand" href="#hero">CineAI</a>
      <div class="topbar__links">
        
          v-for="item in navItems"
          :key="item.href"
          class="topbar__link"
          :class="{ 'topbar__link--active': item.href === activeLink }"
          :href="item.href"
        >
          {{ item.label }}
        </a>
      </div>
    </div>
    <div class="topbar__actions">
      <button class="icon-button" aria-label="Search">
        <span class="material-symbols-outlined">search</span>
      </button>
      <button class="button button--solid">Sign In</button>
    </div>
  </nav>
</template>