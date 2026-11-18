
import api from './api'

export async function getTreks(search = '') {
  const response = await api.get('/treks/', {
    params: search ? { search } : {},
  })
  return response.data
}

export async function createTrek(trekData) {
  const response = await api.post('/treks/', trekData)
  return response.data
}

export async function updateTrek(trekId, trekData) {
  const response = await api.put(`/treks/${trekId}`, trekData)
  return response.data
}

export async function deleteTrek(trekId) {
  const response = await api.delete(`/treks/${trekId}`)
  return response.data
}
