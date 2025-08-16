import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import ResultView from '../views/ResultView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
      meta: {
        title: 'UnblurAI - 文字去模糊识别'
      }
    },
    {
      path: '/result',
      name: 'result',
      component: ResultView,
      meta: {
        title: 'UnblurAI - 识别结果'
      }
    },
  ],
})

export default router
