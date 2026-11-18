
<script setup>
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
</script>

<template>
  <nav class="navbar bg-white border-bottom px-3">
    <div class="container-fluid">
      <span class="navbar-brand fw-semibold">
        Trekking Management Application
      </span>

      <div class="d-flex align-items-center gap-2">
        <span class="text-muted small">
          {{ authStore.user?.name }}
        </span>
        <span class="badge bg-secondary">
          {{ authStore.userRole }}
        </span>
      </div>
    </div>
  </nav>
</template>
