import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/dashboard' },
    { path: '/dashboard', name: 'Dashboard', component: () => import('@/views/DashboardView.vue') },
    { path: '/missions', name: 'Missions', component: () => import('@/views/MissionsView.vue') },
    { path: '/telemetry', name: 'Telemetry', component: () => import('@/views/TelemetryView.vue') },
    { path: '/system/settings', name: 'SystemSettings', component: () => import('@/views/SystemSettingsView.vue') },
  ],
})

export default router
