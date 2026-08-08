/**
 * Events API Client
 * Handles all API calls related to community events
 */
import api from './client'

export const eventsAPI = {
  /**
   * Get upcoming active events
   * @param {number} limit - Maximum number of events to return (1-20)
   * @returns {Promise<Array>} List of upcoming events
   */
  getUpcoming: (limit = 5) => {
    return api.get(`/events/upcoming?limit=${limit}`)
  },

  /**
   * Get all events with optional filters
   * @param {Object} params - Filter parameters
   * @param {number} params.skip - Number of records to skip
   * @param {number} params.limit - Maximum number of records
   * @param {string} params.event_type - Filter by event type
   * @param {boolean} params.is_active - Filter by active status
   * @param {boolean} params.include_past - Include past events
   * @returns {Promise<Object>} Object with events array and total count
   */
  getAll: (params = {}) => {
    return api.get('/events', { params })
  },

  /**
   * Get event by ID
   * @param {number} id - Event ID
   * @returns {Promise<Object>} Event object
   */
  getById: (id) => {
    return api.get(`/events/${id}`)
  },

  /**
   * Create a new event (Admin only)
   * @param {Object} data - Event data
   * @returns {Promise<Object>} Created event
   */
  create: (data) => {
    return api.post('/events', data)
  },

  /**
   * Update an event (Admin only)
   * @param {number} id - Event ID
   * @param {Object} data - Updated event data
   * @returns {Promise<Object>} Updated event
   */
  update: (id, data) => {
    return api.put(`/events/${id}`, data)
  },

  /**
   * Delete an event (Admin only)
   * @param {number} id - Event ID
   * @returns {Promise<void>}
   */
  delete: (id) => {
    return api.delete(`/events/${id}`)
  }
}

