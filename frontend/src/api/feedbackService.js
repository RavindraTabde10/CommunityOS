import api from './client'

const feedbackService = {
  create: (data) => api.post('/feedback', data),
  getAll: (params = {}) => api.get('/feedback', { params }),
  edit: (id, data) => api.patch(`/feedback/${id}`, data),
  update: (id, data) => api.put(`/feedback/${id}`, data),
  delete: (id) => api.delete(`/feedback/${id}`),
}

export default feedbackService
