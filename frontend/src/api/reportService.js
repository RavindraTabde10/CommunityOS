import apiClient from './client'

const reportService = {
  getDashboardStats:       (params = {}) => apiClient.get('/reports/dashboard',    { params }).then(r => r.data),
  getIssueAnalytics:       (params = {}) => apiClient.get('/reports/issues',       { params }).then(r => r.data),
  getContractorPerformance:(params = {}) => apiClient.get('/reports/contractors',  { params }).then(r => r.data),
  getAssetUsage:           (params = {}) => apiClient.get('/reports/assets',       { params }).then(r => r.data),
  exportReport: (data) =>
    apiClient.post('/reports/export', data, {
      responseType: data.format === 'csv' ? 'blob' : 'json',
    }).then(r => r.data),
}

export default reportService
