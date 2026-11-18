
import { defineStore } from 'pinia'
import { loginUser } from '../services/auth'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('access_token') ||
           sessionStorage.getItem('access_token') || null,

    user: JSON.parse(
      localStorage.getItem('user') ||
      sessionStorage.getItem('user') ||
      'null'
    ),
  }),

  getters: {
    isAuthenticated: (state) => !!state.token,
    userRole: (state) => state.user?.role || null,
  },

  actions: {
    async login(credentials, selectedRole, rememberMe) {
      const data = await loginUser(credentials)

      if (data.user.role !== selectedRole) {
        throw new Error(
          `You selected ${selectedRole}, but this account belongs to ${data.user.role}.`
        )
      }

      this.token = data.access_token
      this.user = data.user

      // Clear previous login data
      localStorage.removeItem('access_token')
      localStorage.removeItem('user')
      sessionStorage.removeItem('access_token')
      sessionStorage.removeItem('user')

      // Remember me controls storage duration
      const storage = rememberMe ? localStorage : sessionStorage

      storage.setItem('access_token', data.access_token)
      storage.setItem('user', JSON.stringify(data.user))

      return data
    },

    logout() {
      this.token = null
      this.user = null

      localStorage.removeItem('access_token')
      localStorage.removeItem('user')
      sessionStorage.removeItem('access_token')
      sessionStorage.removeItem('user')
    },
  },
})
