import apiClient from './client'

/**
 * Issue Service
 * Handles all API calls related to issues
 */

const issueService = {
  /**
   * Get all issues with optional filters
   * @param {Object} params - Query parameters
   * @param {number} params.skip - Number of records to skip
   * @param {number} params.limit - Number of records to return
   * @param {string} params.status - Filter by status
   * @param {string} params.category - Filter by category
   * @param {string} params.priority - Filter by priority
   * @param {string} params.search - Search term
   * @returns {Promise} Array of issues
   */
  getIssues: async (params = {}) => {
    const response = await apiClient.get('/issues', { params })
    return response.data
  },

  /**
   * Get issue by ID
   * @param {string} id - Issue ID
   * @returns {Promise} Issue object
   */
  getIssueById: async (id) => {
    const response = await apiClient.get(`/issues/${id}`)
    return response.data
  },

  /**
   * Create new issue
   * @param {Object} issueData - Issue data
   * @returns {Promise} Created issue object
   */
  createIssue: async (issueData) => {
    const response = await apiClient.post('/issues', issueData)
    return response.data
  },

  /**
   * Update issue
   * @param {string} id - Issue ID
   * @param {Object} issueData - Updated issue data
   * @returns {Promise} Updated issue object
   */
  updateIssue: async (id, issueData) => {
    const response = await apiClient.put(`/issues/${id}`, issueData)
    return response.data
  },

  /**
   * Delete issue
   * @param {string} id - Issue ID
   * @returns {Promise} Deletion confirmation
   */
  deleteIssue: async (id) => {
    const response = await apiClient.delete(`/issues/${id}`)
    return response.data
  },

  /**
   * Get issue statistics
   * @returns {Promise} Statistics object
   */
  getStatistics: async () => {
    const issues = await issueService.getIssues({ limit: 1000 })
    
    const stats = {
      total: issues.length,
      open: issues.filter(issue => issue.status === 'open').length,
      in_progress: issues.filter(issue => issue.status === 'in_progress').length,
      resolved: issues.filter(issue => issue.status === 'resolved').length,
      closed: issues.filter(issue => issue.status === 'closed').length,
      high_priority: issues.filter(issue => issue.priority === 'high' || issue.priority === 'critical').length,
    }
    
    return stats
  },

  /**
   * Get recent issues
   * @param {number} limit - Number of issues to return
   * @returns {Promise} Array of recent issues
   */
  getRecentIssues: async (limit = 5) => {
    const response = await apiClient.get('/issues', { 
      params: { skip: 0, limit } 
    })
    return response.data
  },

  /**
   * Upload photos for an issue
   * @param {string} issueId - Issue ID
   * @param {Array} photoFiles - Array of File objects
   * @returns {Promise} Array of uploaded photo objects
   */
  uploadPhotos: async (issueId, photoFiles) => {
    const formData = new FormData()
    photoFiles.forEach(file => {
      formData.append('files', file)
    })

    const response = await apiClient.post(`/issues/${issueId}/photos`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  /**
   * Get photos for an issue
   * @param {string} issueId - Issue ID
   * @returns {Promise} Array of photo objects
   */
  getPhotos: async (issueId) => {
    const response = await apiClient.get(`/issues/${issueId}/photos`)
    return response.data
  },

  /**
   * Delete a photo
   * @param {string} photoId - Photo ID
   * @returns {Promise} Deletion confirmation
   */
  deletePhoto: async (photoId) => {
    const response = await apiClient.delete(`/photos/${photoId}`)
    return response.data
  },
}

export default issueService
