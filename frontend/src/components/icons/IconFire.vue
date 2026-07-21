<template>
  <svg :fill="fill" :stroke="stroke" viewBox="0 0 20 20" width="20" height="20">
    <path stroke="currentColor" d="M16.667 11.56c0-6.39-6.248-9.366-6.248-9.366 0 3.117.784 7.805-1.56 7.805-1.56 0-1.951-1.556-1.951-4.294 0 0-2.741 2.325-2.741 5.865s2.737 6.236 6.252 6.236c3.515 0 6.248-2.71 6.248-6.246Z" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.25"></path>
  </svg>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
export default defineComponent({
  name: "IconFire",
  props: {
    fill: {
      type: String,
      default: 'none'
    },
    stroke: {
      type: String,
      default: 'currentColor'
    }
  }
})
</script>

<style scoped>

</style>