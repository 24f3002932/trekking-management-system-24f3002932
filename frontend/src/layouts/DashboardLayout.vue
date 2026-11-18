
<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import TopNavbar from '../components/TopNavbar.vue'
import Sidebar from '../components/Sidebar.vue'

const authStore = useAuthStore()
const router = useRouter()

function handleLogout() {
  authStore.logout()
  router.push('/')
}
</script>

<template>
  <div class="dashboard-layout">
    <TopNavbar />

    <div class="d-flex">
      <Sidebar />

      <main class="flex-grow-1 dashboard-content">
        <div class="d-flex justify-content-end mb-3">
          <button class="btn btn-outline-danger btn-sm" @click="handleLogout">
            Logout
          </button>
        </div>

        <slot />
      </main>
    </div>
  </div>
</template>

<style scoped>
.dashboard-content {
  min-width: 0;
  padding: 20px;
  background-color: #f8f9fa;
  min-height: calc(100vh - 57px);
}
</style>
