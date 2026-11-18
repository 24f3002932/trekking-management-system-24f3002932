import api from './api'
export const getMyBookings = async () => (await api.get('/bookings/my-bookings')).data
export const bookTrek = async (trekId) => (await api.post(`/bookings/${trekId}`)).data
export const cancelBooking = async (bookingId) => (await api.put(`/bookings/${bookingId}/cancel`)).data
export const getHistory = async () => (await api.get('/bookings/history')).data
export const getMyProfile = async () => (await api.get('/auth/profile')).data
export const updateMyProfile = async (data) => (await api.put('/auth/profile', data)).data
export const getNotifications = async () => (await api.get('/auth/notifications')).data
export const markNotificationRead = async (id) => (await api.put(`/auth/notifications/${id}/read`)).data
