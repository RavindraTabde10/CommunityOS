/**
 * Committee Service
 * API client for committee member operations
 */
import apiClient from './client'

const committeeService = {
  /**
   * Get active committee members (public - all authenticated users)
   * @returns {Promise<Array>} List of active committee members
   */
  getActiveMembers: async () => {
    const response = await apiClient.get('/committee/active')
    return response.data
  },

  /**
   * Get all committee members (admin only)
   * @returns {Promise<Array>} List of all committee members
   */
  getAllMembers: async () => {
    const response = await apiClient.get('/committee')
    return response.data
  },

  /**
   * Get committee member by ID
   * @param {number} id - Committee member ID
   * @returns {Promise<Object>} Committee member details
   */
  getMember: async (id) => {
    const response = await apiClient.get(`/committee/${id}`)
    return response.data
  },

  /**
   * Create committee member (admin only)
   * @param {Object} data - Committee member data
   * @returns {Promise<Object>} Created committee member
   */
  createMember: async (data) => {
    const response = await apiClient.post('/committee', data)
    return response.data
  },

  /**
   * Update committee member (admin only)
   * @param {number} id - Committee member ID
   * @param {Object} data - Update data
   * @returns {Promise<Object>} Updated committee member
   */
  updateMember: async (id, data) => {
    const response = await apiClient.put(`/committee/${id}`, data)
    return response.data
  },

  /**
   * Delete committee member (admin only)
   * @param {number} id - Committee member ID
   * @returns {Promise<void>}
   */
  deleteMember: async (id) => {
    await apiClient.delete(`/committee/${id}`)
  }
}

export default committeeService
