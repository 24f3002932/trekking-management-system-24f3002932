import api from './api'

export const getStaff = async (search='') => (await api.get('/staff/', {params: search ? {search} : {}})).data
export const createStaff = async (data) => (await api.post('/staff/', data)).data
export const updateStaff = async (id, data) => (await api.put(`/staff/${id}`, data)).data
export const updateStaffStatus = async (id, data) => (await api.put(`/staff/${id}/status`, data)).data
export const getTrekkers = async (search='') => (await api.get('/users/', {params: search ? {search} : {}})).data
export const updateTrekkerStatus = async (id, data) => (await api.put(`/users/${id}/status`, data)).data
export const getAdminBookings = async (search='') => (await api.get('/admin/bookings', {params: search ? {search} : {}})).data
export const cancelAdminBooking = async (id) => (await api.put(`/admin/bookings/${id}/cancel`)).data
export const assignStaff = async (trekId, staffId) => (await api.post(`/treks/${trekId}/staff`, {staff_id: staffId})).data
export const getAssignedStaff = async (trekId) => (await api.get(`/treks/${trekId}/staff`)).data
export const removeAssignedStaff = async (trekId, staffId) => (await api.delete(`/treks/${trekId}/staff/${staffId}`)).data
