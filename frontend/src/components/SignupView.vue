<script setup lang="ts">
import { api, type ValidationError } from "@/api/client";
import axios from "axios";
import { ref } from "vue";

const errors = ref<{ loc: string | number; msg: string }[]>([]);

const form = ref({
  name: "",
  password: "",
});

async function handleSubmit() {
  try {
    const res = await api.post("/api/auth/signup", form.value);
    console.log(res);
  } catch (err) {
    if (axios.isAxiosError(err) && err.response?.status === 422) {
      // 422 エラーの場合
      errors.value = err.response.data.detail.map((res: ValidationError) => ({
        loc: res.loc[res.loc.length - 1],
        msg: res.msg,
      }));
      console.log(errors.value);
    }
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
