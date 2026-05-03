import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('@/components/views/HomeView.vue'),
    },
    {
      path: '/music',
      name: 'music',
      component: () => import('@/components/views/MusicView.vue'),
    },
    {
      path: '/library',
      name: 'library',
      component: () => import('@/components/views/LibraryView.vue'),
    },
    {
      path: '/obd',
      name: 'obd',
      component: () => import('@/components/views/OBDView.vue'),
    },
    {
      path: '/maps',
      name: 'maps',
      component: () => import('@/components/views/MapsView.vue'),
    },
    {
      path: '/settings',
      name: 'settings',
      component: () => import('@/components/views/SettingsView.vue'),
    },
  ],
})

export default router