
<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import DashboardLayout from '../layouts/DashboardLayout.vue'
import { createStaff } from '../services/staff'

const router = useRouter()

const form = ref({
  name: '',
  email: '',
  password: '',
  phone: '',
  experience: 0,
  specialization: '',
  contact: '',
})

const loading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

async function handleSubmit() {
  errorMessage.value = ''
  successMessage.value = ''

  if (form.value.password.length < 8) {
    errorMessage.value = 'Password must contain at least 8 characters.'
    return
  }

  loading.value = true

  try {
    const response = await createStaff({
      ...form.value,
      experience: Number(form.value.experience),
    })

    successMessage.value = response.message

    form.value = {
      name: '',
      email: '',
      password: '',
      phone: '',
      experience: 0,
      specialization: '',
      contact: '',
    }
  } catch (error) {
    errorMessage.value =
      error.response?.data?.message || 'Unable to create staff account.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <DashboardLayout>
    <div class="container-fluid p-0">

      <div class="d-flex justify-content-between align-items-center mb-4">
        <h3 class="fw-semibold mb-0">Create Staff</h3>
        <button
          class="btn btn-outline-secondary"
          @click="router.push('/admin')"
        >
          Back to Dashboard
        </button>
      </div>

      <div class="card border shadow-sm">
        <div class="card-header bg-white py-3">
          <h5 class="mb-0">Staff Registration Form</h5>
        </div>

        <div class="card-body">

          <div v-if="errorMessage" class="alert alert-danger">
            {{ errorMessage }}
          </div>

          <div v-if="successMessage" class="alert alert-success">
            {{ successMessage }}
          </div>

          <form @submit.prevent="handleSubmit">
            <div class="row g-3">

              <div class="col-md-6">
                <label class="form-label">Full Name *</label>
                <input
                  v-model="form.name"
                  type="text"
                  class="form-control"
                  placeholder="Enter full name"
                  required
                />
              </div>

              <div class="col-md-6">
                <label class="form-label">Email Address *</label>
                <input
                  v-model="form.email"
                  type="email"
                  class="form-control"
                  placeholder="Enter email"
                  required
                />
              </div>

              <div class="col-md-6">
                <label class="form-label">Password *</label>
                <input
                  v-model="form.password"
                  type="password"
                  class="form-control"
                  minlength="8"
                  placeholder="Minimum 8 characters"
                  required
                />
              </div>

              <div class="col-md-6">
                <label class="form-label">Phone Number</label>
                <input
                  v-model="form.phone"
                  type="tel"
                  class="form-control"
                  placeholder="Enter phone number"
                />
              </div>

              <div class="col-md-6">
                <label class="form-label">Experience (Years)</label>
                <input
                  v-model.number="form.experience"
                  type="number"
                  min="0"
                  class="form-control"
                />
              </div>

              <div class="col-md-6">
                <label class="form-label">Specialization</label>
                <input
                  v-model="form.specialization"
                  type="text"
                  class="form-control"
                  placeholder="e.g. Mountain Trekking"
                />
              </div>

              <div class="col-md-12">
                <label class="form-label">Contact Details</label>
                <input
                  v-model="form.contact"
                  type="text"
                  class="form-control"
                  placeholder="Additional contact details"
                />
              </div>

            </div>

            <div class="mt-4 d-flex gap-2">
              <button
                type="submit"
                class="btn btn-primary"
                :disabled="loading"
              >
                {{ loading ? 'Creating...' : 'Create Staff Account' }}
              </button>

              <button
                type="reset"
                class="btn btn-outline-secondary"
                @click="form = {
                  name: '',
                  email: '',
                  password: '',
                  phone: '',
                  experience: 0,
                  specialization: '',
                  contact: ''
                }"
              >
                Reset
              </button>
            </div>
          </form>

        </div>
      </div>

    </div>
  </DashboardLayout>
</template>
