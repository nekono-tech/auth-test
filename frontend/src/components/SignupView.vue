<script setup lang="ts">
import { api } from "@/api/client";
import { ref } from "vue";

const form = ref({
  name: "",
  password: "",
});

async function handleSubmit() {
  try {
    const res = await api.post("/api/auth/signup", form.value);
    console.log(res);
  } catch (err) {
    console.error(err);
  }
}
</script>

<template>
  <h1>Signup View</h1>
  <form @submit.prevent="handleSubmit" method="post">
    <div>
      <label for="name">Name:</label>
      <input type="text" name="name" id="name" v-model="form.name" />
    </div>
    <div>
      <label for="password">Password:</label>
      <input
        type="password"
        name="password"
        id="password"
        v-model="form.password"
      />
    </div>
    <button type="submit">送信</button>
  </form>
</template>

<style scoped></style>
