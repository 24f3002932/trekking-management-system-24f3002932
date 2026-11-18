
import api from './api'

export async function createStaff(staffData) {
  const response = await api.post('/staff/', staffData)
  return response.data
}

export async function getStaff(search = '') {
  const response = await api.get('/staff/', {
    params: search ? { search } : {},
  })
  return response.data
}

export async function updateStaff(staffId, staffData) {
  const response = await api.put(`/staff/${staffId}`, staffData)
  return response.data
}

export async function updateStaffStatus(staffId, statusData) {
  const response = await api.put(`/staff/${staffId}/status`, statusData)
  return response.data
}

