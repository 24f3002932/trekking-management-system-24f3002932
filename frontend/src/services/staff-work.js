import api from './api'
export const getMyTreks = async () => (await api.get('/staff/my-treks')).data
export const getParticipants = async (trekId) => (await api.get(`/staff/my-treks/${trekId}/participants`)).data
export const manageAssignedTrek = async (trekId, data) => (await api.put(`/staff/my-treks/${trekId}/manage`, data)).data
