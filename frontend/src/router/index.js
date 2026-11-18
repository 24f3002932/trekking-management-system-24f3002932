import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import AdminDashboard from '../views/AdminDashboard.vue'
import StaffDashboard from '../views/StaffDashboard.vue'
import TrekkerDashboard from '../views/TrekkerDashboard.vue'
import ManageTreksView from '../views/ManageTreksView.vue'
import CreateStaffView from '../views/CreateStaffView.vue'
import WorkspaceView from '../views/WorkspaceView.vue'
import { useAuthStore } from '../stores/auth'

const routes = [
  { path: '/', name: 'login', component: LoginView, meta: { guestOnly: true } },
  { path: '/register', name: 'register', component: RegisterView, meta: { guestOnly: true } },
  { path: '/admin', name: 'admin', component: AdminDashboard, meta: { requiresAuth: true, role: 'admin' } },
  { path: '/staff', name: 'staff', component: StaffDashboard, meta: { requiresAuth: true, role: 'staff' } },
  { path: '/trekker', name: 'trekker', component: TrekkerDashboard, meta: { requiresAuth: true, role: 'trekker' } },
  { path: '/admin/treks', name: 'manage-treks', component: ManageTreksView, meta: { requiresAuth: true, role: 'admin' } },
  { path: '/admin/create-staff', name: 'create-staff', component: CreateStaffView, meta: { requiresAuth: true, role: 'admin' } },
  { path: '/admin/staff', name: 'manage-staff', component: WorkspaceView, meta: { requiresAuth: true, role: 'admin', screen: 'manage-staff' } },
  { path: '/admin/trekkers', name: 'manage-trekkers', component: WorkspaceView, meta: { requiresAuth: true, role: 'admin', screen: 'manage-trekkers' } },
  { path: '/admin/bookings', name: 'admin-bookings', component: WorkspaceView, meta: { requiresAuth: true, role: 'admin', screen: 'admin-bookings' } },
  { path: '/staff/my-treks', name: 'staff-treks', component: WorkspaceView, meta: { requiresAuth: true, role: 'staff', screen: 'staff-treks' } },
  { path: '/trekker/browse', name: 'browse-treks', component: WorkspaceView, meta: { requiresAuth: true, role: 'trekker', screen: 'browse-treks' } },
  { path: '/trekker/bookings', name: 'my-bookings', component: WorkspaceView, meta: { requiresAuth: true, role: 'trekker', screen: 'my-bookings' } },
  { path: '/trekker/history', name: 'history', component: WorkspaceView, meta: { requiresAuth: true, role: 'trekker', screen: 'history' } },
  { path: '/trekker/profile', name: 'profile', component: WorkspaceView, meta: { requiresAuth: true, role: 'trekker', screen: 'profile' } },
  { path: '/trekker/notifications', name: 'notifications', component: WorkspaceView, meta: { requiresAuth: true, role: 'trekker', screen: 'notifications' } },
]

const router = createRouter({ history: createWebHistory(import.meta.env.BASE_URL), routes })

router.beforeEach((to) => {
  const authStore = useAuthStore()
  if (to.meta.requiresAuth && !authStore.isAuthenticated) return '/'
  if (to.meta.requiresAuth && to.meta.role !== authStore.userRole) {
    if (authStore.userRole === 'admin') return '/admin'
    if (authStore.userRole === 'staff') return '/staff'
    if (authStore.userRole === 'trekker') return '/trekker'
    return '/'
  }
  if (to.meta.guestOnly && authStore.isAuthenticated) {
    if (authStore.userRole === 'admin') return '/admin'
    if (authStore.userRole === 'staff') return '/staff'
    if (authStore.userRole === 'trekker') return '/trekker'
  }
})

export default router
