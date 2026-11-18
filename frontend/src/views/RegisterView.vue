
<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { registerUser } from '../services/auth'

const router = useRouter()

const name = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const phone = ref('')

const loading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

async function handleRegister() {
  errorMessage.value = ''
  successMessage.value = ''

  if (password.value !== confirmPassword.value) {
    errorMessage.value = 'Passwords do not match.'
    return
  }

  if (password.value.length < 8) {
    errorMessage.value = 'Password must contain at least 8 characters.'
    return
  }

  loading.value = true

  try {
    const response = await registerUser({
      name: name.value,
      email: email.value,
      password: password.value,
      phone: phone.value,
    })

    successMessage.value = response.message

    // Redirect to login after successful registration
    setTimeout(() => {
      router.push('/')
    }, 1500)

  } catch (error) {
    errorMessage.value =
      error.response?.data?.message ||
      'Registration failed. Please try again.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="register-page container-fluid">
    <div class="row min-vh-100 align-items-center justify-content-center p-3">

      <div class="col-12 col-md-7 col-lg-5">
        <div class="card border shadow-sm">
          <div class="card-body p-4 p-md-5">

            <div class="text-center mb-4">
              <h3 class="fw-bold">Create User Account</h3>
              <p class="text-muted">Register as a Trekker</p>
            </div>

            <div v-if="errorMessage" class="alert alert-danger">
              {{ errorMessage }}
            </div>

            <div v-if="successMessage" class="alert alert-success">
              {{ successMessage }}
            </div>

            <form @submit.prevent="handleRegister">

              <div class="mb-3">
                <label class="form-label">Full Name</label>
                <input
                  type="text"
                  class="form-control"
                  placeholder="Enter your full name"
                  v-model="name"
                  required
                />
              </div>

              <div class="mb-3">
                <label class="form-label">Email address</label>
                <input
                  type="email"
                  class="form-control"
                  placeholder="Enter your email"
                  v-model="email"
                  required
                />
              </div>

              <div class="mb-3">
                <label class="form-label">Password</label>
                <input
                  type="password"
                  class="form-control"
                  placeholder="Create a password"
                  v-model="password"
                  minlength="8"
                  required
                />
              </div>

              <div class="mb-3">
                <label class="form-label">Confirm Password</label>
                <input
                  type="password"
                  class="form-control"
                  placeholder="Confirm your password"
                  v-model="confirmPassword"
                  minlength="8"
                  required
                />
              </div>

              <div class="mb-4">
                <label class="form-label">Contact Number</label>
                <input
                  type="tel"
                  class="form-control"
                  placeholder="Enter your contact number"
                  v-model="phone"
                  required
                />
              </div>

              <button
                type="submit"
                class="btn btn-primary w-100"
                :disabled="loading"
              >
                {{ loading ? 'Registering...' : 'Register' }}
              </button>

            </form>

            <div class="text-center mt-4">
              <p class="small mb-1">Already have an account?</p>
              <RouterLink to="/">
                Login here
              </RouterLink>
            </div>

          </div>
        </div>

        <div class="alert alert-info small mt-3">
          Note: Only users (Trekkers) can register themselves.
          Trekking Staff are created by Admin.
        </div>

      </div>
    </div>
  </div>
</template>

<style scoped>
.register-page {
  background-color: #f5f6f8;
}
</style>
