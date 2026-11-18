
<script setup>
import { ref } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()

const selectedRole = ref('trekker')
const email = ref('')
const password = ref('')
const rememberMe = ref(false)

const loading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

async function handleLogin() {
  errorMessage.value = ''
  successMessage.value = ''
  loading.value = true

  try {
    await authStore.login(
      {
        email: email.value,
        password: password.value,
      },
      selectedRole.value,
      rememberMe.value
    )

    successMessage.value = 'Login successful!'
    if (authStore.userRole === 'admin') {
        router.push('/admin')
    } else if (authStore.userRole === 'staff') {
        router.push('/staff')
    } else if (authStore.userRole === 'trekker') {
        router.push('/trekker')
    }

    successMessage.value = 'Login successful!'

    console.log('Logged in user:', authStore.user)
    console.log('User role:', authStore.userRole)

  } catch (error) {
    errorMessage.value =
      error.response?.data?.message ||
      error.message ||
      'Something went wrong. Please try again.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-page container-fluid">
    <div class="row min-vh-100 align-items-center justify-content-center p-3">

      <div class="col-12 col-lg-9">
        <div class="row bg-white border rounded-3 overflow-hidden shadow-sm">

          <!-- Left Section -->
          <div class="col-md-5 p-4 border-end">

            <h5 class="fw-bold mb-2">
              Trekking Management Application
            </h5>

            <p class="text-muted small mb-4">
              Select your role to continue
            </p>

            <h6 class="fw-semibold mb-3">ROLES</h6>

            <div class="d-grid gap-3">

              <label class="role-option">
                <input type="radio" value="admin" v-model="selectedRole">
                <span>Admin</span>
              </label>

              <label class="role-option">
                <input type="radio" value="staff" v-model="selectedRole">
                <span>Trekking Staff</span>
              </label>

              <label class="role-option">
                <input type="radio" value="trekker" v-model="selectedRole">
                <span>User (Trekker)</span>
              </label>

            </div>

            <div class="alert alert-info small mt-4 mb-0">
              Note: Only users (Trekkers) can register themselves.
              Trekking Staff are created by Admin.
            </div>

          </div>

          <!-- Right Section -->
          <div class="col-md-7 p-4 p-md-5">

            <div class="text-center mb-4">
              <h3 class="fw-bold">Welcome Back!</h3>
              <p class="text-muted">Login to your account</p>
            </div>

            <div v-if="errorMessage" class="alert alert-danger">
              {{ errorMessage }}
            </div>

            <div v-if="successMessage" class="alert alert-success">
              {{ successMessage }}
            </div>

            <form @submit.prevent="handleLogin">

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
                  placeholder="Enter your password"
                  v-model="password"
                  required
                />
              </div>

              <div class="form-check mb-3">
                <input
                  type="checkbox"
                  class="form-check-input"
                  id="remember"
                  v-model="rememberMe"
                />
                <label class="form-check-label" for="remember">
                  Remember me
                </label>
              </div>

              <button
                type="submit"
                class="btn btn-primary w-100"
                :disabled="loading"
              >
                {{ loading ? 'Logging in...' : 'Login' }}
              </button>

            </form>

            <div class="text-center mt-4">
              <p class="small mb-1">Don't have an account?</p>
              <RouterLink to="/register">
                Register as User (Trekker)
              </RouterLink>
            </div>

          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<style scoped>
.login-page {
  background-color: #f5f6f8;
}

.role-option {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 13px;
  border: 1px solid #dee2e6;
  border-radius: 5px;
  cursor: pointer;
}

.role-option:hover {
  border-color: #0d6efd;
  background-color: #f8f9ff;
}

.role-option input {
  accent-color: #0d6efd;
}
</style>
