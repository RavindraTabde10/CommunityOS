/**
 * Polls API client
 * Handles poll and voting endpoints.
 */
import api from './client'

export const pollsAPI = {
  getAll: (params = {}) => {
    return api.get('/polls', { params })
  },

  create: (data) => {
    return api.post('/polls', data)
  },

  getById: (id) => {
    return api.get(`/polls/${id}`)
  },

  delete: (id) => {
    return api.delete(`/polls/${id}`)
  },

  update: (id, data) => {
    return api.put(`/polls/${id}`, data)
  },

  vote: (id, data) => {
    return api.post(`/polls/${id}/vote`, data)
  }
}
