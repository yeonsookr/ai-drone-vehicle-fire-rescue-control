import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/dashboard' },

    // ── 대시보드 ──
    { path: '/dashboard', name: 'Dashboard', component: () => import('@/views/DashboardView.vue') },

    // ── 임무 ──
    { path: '/missions', name: 'Missions', component: () => import('@/views/MissionsView.vue') },

    // ── 관측 ──
    { path: '/telemetry', name: 'Telemetry', component: () => import('@/views/TelemetryView.vue') },
    { path: '/streams', name: 'Streams', component: () => import('@/views/StreamsView.vue') },
    { path: '/detections', name: 'Detections', component: () => import('@/views/DetectionsView.vue') },

    // ── 장비 ──
    { path: '/devices', name: 'Devices', component: () => import('@/views/DevicesView.vue') },
    { path: '/pairings', name: 'Pairings', component: () => import('@/views/PairingsView.vue') },

    // ── 운영 ──
    { path: '/operations/battery', name: 'BatteryStatus', component: () => import('@/views/BatteryView.vue') },
    { path: '/operations/logs', name: 'OperationLogs', component: () => import('@/views/OperationLogsView.vue') },

    // ── 시스템 ──
    { path: '/system/server', name: 'ServerStatus', component: () => import('@/views/ServerStatusView.vue') },
    { path: '/system/settings', name: 'SystemSettings', component: () => import('@/views/SystemSettingsView.vue') },
  ],
})

export default router
