
import api from './api'

export async function getAdminDashboard() {
  const response = await api.get('/admin/dashboard')
  return response.data
}

export async function getAdminBookings() {
  const response = await api.get('/admin/bookings')
  return response.data
}
