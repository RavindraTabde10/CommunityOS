import apiClient from './client'

const waterTankerService = {
  // Suppliers
  getSuppliers:    (params = {}) => apiClient.get('/water-tanker/suppliers', { params }).then(r => r.data),
  createSupplier:  (data)        => apiClient.post('/water-tanker/suppliers', data).then(r => r.data),
  updateSupplier:  (id, data)    => apiClient.put(`/water-tanker/suppliers/${id}`, data).then(r => r.data),
  deleteSupplier:  (id)          => apiClient.delete(`/water-tanker/suppliers/${id}`),

  // Orders
  getOrders:  (params = {}) => apiClient.get('/water-tanker/orders', { params }).then(r => r.data),
  createOrder:(data)         => apiClient.post('/water-tanker/orders', data).then(r => r.data),
  updateOrder:(id, data)     => apiClient.put(`/water-tanker/orders/${id}`, data).then(r => r.data),
  cancelOrder:(id)           => apiClient.delete(`/water-tanker/orders/${id}`).then(r => r.data),
}

export default waterTankerService
