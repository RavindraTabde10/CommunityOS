import api from './client'

const visitorService = {
  logVisitor: (data) => api.post('/visitors', data),
  getAll: (params = {}) => api.get('/visitors', { params }),
  getMyVisitors: () => api.get('/visitors/my-visitors'),
  getPendingForMe: () => api.get('/visitors/my-visitors/pending'),
  getById: (id) => api.get(`/visitors/${id}`),
  editVisitor: (id, data) => api.patch(`/visitors/${id}`, data),
  updateStatus: (id, status) => api.patch(`/visitors/${id}/status`, { status }),
  residentByUnit: (unit) => api.get(`/visitors/resident-by-unit/${encodeURIComponent(unit)}`),
}

export default visitorService
