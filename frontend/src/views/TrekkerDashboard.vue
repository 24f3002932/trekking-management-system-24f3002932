<script setup>
import { useAuthStore } from '../stores/auth'
import DashboardLayout from '../layouts/DashboardLayout.vue'
const authStore = useAuthStore()
</script>
<template>
  <DashboardLayout>
    <div class="container-fluid p-0">
      <h3 class="fw-semibold mb-2">Trekker Dashboard</h3>
      <p class="text-muted mb-4">Welcome, {{ authStore.user?.name }}. Discover trekking experiences, manage your bookings and review your trekking history.</p>
      <div class="row g-3">
        <div class="col-12 col-md-6 col-xl-3"><div class="card border shadow-sm h-100"><div class="card-body"><h5>Browse Treks</h5><RouterLink class="btn btn-primary btn-sm mt-2" to="/trekker/browse">Open</RouterLink></div></div></div><div class="col-12 col-md-6 col-xl-3"><div class="card border shadow-sm h-100"><div class="card-body"><h5>My Bookings</h5><RouterLink class="btn btn-primary btn-sm mt-2" to="/trekker/bookings">Open</RouterLink></div></div></div><div class="col-12 col-md-6 col-xl-3"><div class="card border shadow-sm h-100"><div class="card-body"><h5>Trekking History</h5><RouterLink class="btn btn-primary btn-sm mt-2" to="/trekker/history">Open</RouterLink></div></div></div><div class="col-12 col-md-6 col-xl-3"><div class="card border shadow-sm h-100"><div class="card-body"><h5>My Profile</h5><RouterLink class="btn btn-primary btn-sm mt-2" to="/trekker/profile">Open</RouterLink></div></div></div>
      </div>
    </div>
  </DashboardLayout>
</template>
