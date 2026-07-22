import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/dashboard' },
    {
      path: '/dashboard',
      name: 'Dashboard',
      component: () => import('@/views/DashboardView.vue'),
    },
    {
      path: '/devices',
      name: 'Devices',
      component: () => import('@/views/DevicesView.vue'),
    },
    {
      path: '/telemetry',
      name: 'Telemetry',
      component: () => import('@/views/TelemetryView.vue'),
    },
    {
      path: '/detections',
      name: 'Detections',
      component: () => import('@/views/DetectionsView.vue'),
    },
    {
      path: '/missions',
      name: 'Missions',
      component: () => import('@/views/MissionsView.vue'),
    },
  ],
})

export default router
