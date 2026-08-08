import client from './client'

/**
 * Activity Service
 * Handles all activity timeline API calls
 */

/**
 * Get activity log for an issue
 * @param {string} issueId - Issue ID
 * @param {number} skip - Pagination offset
 * @param {number} limit - Pagination limit
 * @returns {Promise} Activity list with pagination info
 */
export const getActivityLog = async (issueId, skip = 0, limit = 50) => {
  const response = await client.get(`/issues/${issueId}/activity`, {
    params: { skip, limit }
  })
  return response.data
}
