import apiClient from './client'

const assetService = {
  // ── Assets ──────────────────────────────────────────────────────────────
  getAssets: (params = {}) => apiClient.get('/assets', { params }),
  getAsset: (id) => apiClient.get(`/assets/${id}`),
  createAsset: (data) => apiClient.post('/assets', data),
  updateAsset: (id, data) => apiClient.put(`/assets/${id}`, data),
  deleteAsset: (id) => apiClient.delete(`/assets/${id}`),
  getAssetStats: (id) => apiClient.get(`/assets/${id}/stats`),
  getQRCode: (id) => apiClient.get(`/assets/${id}/qrcode`),
  scanQRCode: (qrCodeData) => apiClient.post('/assets/scan', { qr_code_data: qrCodeData }),

  // ── Bookings ─────────────────────────────────────────────────────────────
  getMyBookings: (params = {}) => apiClient.get('/bookings', { params }),
  getBooking: (id) => apiClient.get(`/bookings/${id}`),
  createBooking: (data) => apiClient.post('/bookings', data),
  updateBooking: (id, data) => apiClient.put(`/bookings/${id}`, data),
  cancelBooking: (id, reason) =>
    apiClient.delete(`/bookings/${id}`, {
      params: reason ? { cancellation_reason: reason } : {},
    }),
  checkIn: (id) => apiClient.post(`/bookings/${id}/checkin`),
  checkOut: (id) => apiClient.post(`/bookings/${id}/checkout`),
  checkAvailability: (assetId, bookingDate, startTime, endTime, numberOfGuests = 1) =>
    apiClient.get(`/bookings/assets/${assetId}/availability`, {
      params: {
        booking_date: bookingDate,
        start_time: startTime,
        end_time: endTime,
        number_of_guests: numberOfGuests,
      },
    }),
  getAssetBookings: (assetId, params = {}) =>
    apiClient.get(`/bookings/assets/${assetId}/bookings`, { params }),
}

export default assetService
