<script setup lang="ts"></script>

<template>
  <nav>
    <RouterLink to="/">Top</RouterLink>
    <RouterLink to="/signup">Signup</RouterLink>
  </nav>
  <RouterView />
</template>

<style scoped>
nav {
  display: flex;
  gap: 10px;
}
</style>
