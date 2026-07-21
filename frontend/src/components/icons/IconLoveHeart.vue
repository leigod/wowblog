<template>
  <svg viewBox="0 0 22 20" :fill="fill" xmlns="http://www.w3.org/2000/svg" @click="handleClick">
    <path
      d="M11 19C12 19 21 14.0002 21 7.00043C21 3.50057 18 1.04405 15 1.00065C13.5 0.978943 12 1.50065 11 3.00059C10 1.50065 8.47405 1.00065 7 1.00065C4 1.00065 1 3.50057 1 7.00043C1 14.0002 10 19 11 19Z"
      :stroke="stroke"
      stroke-width="1.5"
      stroke-linecap="round"
      stroke-linejoin="round"
    ></path>
  </svg>
</template>

<script lang="ts">
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'IconLoveHeart',
  props: {
    fill: {
      type: String,
      default: 'currentColor'
    },
    stroke: {
      type: String,
      default: 'none'
    }
  },
  methods: {
    handleClick() {
      this.$emit('icon-click')
    }
  }
})
</script>
