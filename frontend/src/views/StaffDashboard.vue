<script setup>
import { useAuthStore } from '../stores/auth'
import DashboardLayout from '../layouts/DashboardLayout.vue'
const authStore = useAuthStore()
</script>
<template>
  <DashboardLayout>
    <div class="container-fluid p-0">
      <h3 class="fw-semibold mb-2">Staff Dashboard</h3>
      <p class="text-muted mb-4">Welcome, {{ authStore.user?.name }}. View your assigned treks, update trek availability and manage participants.</p>
      <div class="row g-3">
        <div class="col-12 col-md-6 col-xl-3"><div class="card border shadow-sm h-100"><div class="card-body"><h5>My Assigned Treks</h5><RouterLink class="btn btn-primary btn-sm mt-2" to="/staff/my-treks">Open</RouterLink></div></div></div>
      </div>
    </div>
  </DashboardLayout>
</template>
