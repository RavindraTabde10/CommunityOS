/**
 * Announcement API Service
 * Handles all API calls related to announcements
 */

import apiClient from './client'

const announcementService = {
  /**
   * Get active announcements (all users)
   * @returns {Promise<Array>} List of active announcements
   */
  getActiveAnnouncements: async () => {
    const response = await apiClient.get('/announcements/active')
    return response.data
  },

  /**
   * Get all announcements including inactive (admin only)
   * @param {number} skip - Number of records to skip
   * @param {number} limit - Maximum number of records to return
   * @returns {Promise<Array>} List of all announcements
   */
  getAllAnnouncements: async (skip = 0, limit = 100) => {
    const response = await apiClient.get('/announcements/', {
      params: { skip, limit }
    })
    return response.data
  },

  /**
   * Get single announcement by ID
   * @param {string} announcementId - Announcement UUID
   * @returns {Promise<Object>} Announcement details
   */
  getAnnouncement: async (announcementId) => {
    const response = await apiClient.get(`/announcements/${announcementId}`)
    return response.data
  },

  /**
   * Create new announcement (admin only)
   * @param {Object} announcementData - Announcement creation data
   * @returns {Promise<Object>} Created announcement
   */
  createAnnouncement: async (announcementData) => {
    const response = await apiClient.post('/announcements/', announcementData)
    return response.data
  },

  /**
   * Update announcement (admin only)
   * @param {string} announcementId - Announcement UUID
   * @param {Object} updateData - Fields to update
   * @returns {Promise<Object>} Updated announcement
   */
  updateAnnouncement: async (announcementId, updateData) => {
    const response = await apiClient.put(`/announcements/${announcementId}`, updateData)
    return response.data
  },

  /**
   * Delete announcement (admin only)
   * @param {string} announcementId - Announcement UUID
   * @returns {Promise<void>}
   */
  deleteAnnouncement: async (announcementId) => {
    await apiClient.delete(`/announcements/${announcementId}`)
  }
}

export default announcementService
