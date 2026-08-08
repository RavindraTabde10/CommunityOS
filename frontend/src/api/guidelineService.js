import api from './client'

const guidelineService = {
  getActive: () => api.get('/guidelines/'),
  getAll: () => api.get('/guidelines/all'),
  bulkUpdate: (guidelines) => api.put('/guidelines/bulk', { guidelines }),
}

export default guidelineService
