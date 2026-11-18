
<script setup>
import { ref, onMounted } from 'vue'
import DashboardLayout from '../layouts/DashboardLayout.vue'
import { getAdminDashboard, getAdminBookings } from '../services/admin'

const statistics = ref([
  { title: 'Total Treks', value: 0 },
  { title: 'Total Users', value: 0 },
  { title: 'Total Trekking Staff', value: 0 },
  { title: 'Total Bookings', value: 0 },
])

const bookings = ref([])
const loading = ref(true)
const errorMessage = ref('')

function formatDate(date) {
  if (!date) return '—'

  return new Date(date).toLocaleDateString('en-IN')
}

async function loadDashboard() {
  loading.value = true
  errorMessage.value = ''

  try {
    const [dashboardData, bookingData] = await Promise.all([
      getAdminDashboard(),
      getAdminBookings(),
    ])

    const stats = dashboardData.statistics

    statistics.value = [
      { title: 'Total Treks', value: stats.total_treks },
      { title: 'Total Users', value: stats.total_users },
      { title: 'Total Trekking Staff', value: stats.total_staff },
      { title: 'Total Bookings', value: stats.total_bookings },
    ]

    // Show latest 5 bookings
    bookings.value = bookingData.bookings.slice(0, 5)

  } catch (error) {
    errorMessage.value =
      error.response?.data?.message ||
      'Unable to load dashboard data.'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadDashboard()
})
</script>

<template>
  <DashboardLayout>
    <div class="container-fluid p-0">

      <div class="d-flex justify-content-between align-items-center mb-4">
        <h3 class="fw-semibold mb-0">Dashboard</h3>

        <button
          class="btn btn-outline-primary btn-sm"
          @click="loadDashboard"
          :disabled="loading"
        >
          Refresh
        </button>
      </div>

      <!-- Error message -->
      <div v-if="errorMessage" class="alert alert-danger">
        {{ errorMessage }}
      </div>

      <!-- Statistics -->
      <div class="row g-3 mb-4">

        <div
          v-for="item in statistics"
          :key="item.title"
          class="col-12 col-sm-6 col-xl-3"
        >
          <div class="card border shadow-sm h-100">
            <div class="card-body">
              <p class="text-muted mb-2">
                {{ item.title }}
              </p>

              <h3 class="fw-bold mb-0">
                {{ loading ? '...' : item.value }}
              </h3>
            </div>
          </div>
        </div>

      </div>

      <!-- Recent Bookings -->
      <div class="card border shadow-sm">

        <div class="card-header bg-white py-3">
          <h5 class="mb-0 fw-semibold">Recent Bookings</h5>
        </div>

        <div class="card-body">

          <div v-if="loading" class="text-center py-4">
            Loading bookings...
          </div>

          <div
            v-else-if="!errorMessage && bookings.length === 0"
            class="text-center text-muted py-4"
          >
            No bookings available.
          </div>

          <div v-else-if="bookings.length > 0" class="table-responsive">
            <table class="table table-bordered table-hover mb-0">

              <thead class="table-light">
                <tr>
                  <th>Booking ID</th>
                  <th>User (Trekker)</th>
                  <th>Trek</th>
                  <th>Booking Date</th>
                  <th>Status</th>
                </tr>
              </thead>

              <tbody>
                <tr v-for="booking in bookings" :key="booking.booking_id">
                  <td>{{ booking.booking_id }}</td>
                  <td>{{ booking.user.name }}</td>
                  <td>{{ booking.trek.name }}</td>
                  <td>{{ formatDate(booking.booking_date) }}</td>
                  <td>{{ booking.status }}</td>
                </tr>
              </tbody>

            </table>
          </div>

        </div>
      </div>

    </div>
  </DashboardLayout>
</template>
