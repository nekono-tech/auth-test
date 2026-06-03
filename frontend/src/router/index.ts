import HomeView from "@/components/HomeView.vue";
import SignupView from "@/components/SignupView.vue";
import { createRouter, createWebHistory } from "vue-router";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      component: HomeView,
    },
    {
      path: "/signup",
      component: SignupView,
    },
  ],
});

export default router;
