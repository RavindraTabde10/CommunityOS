import client from './client'

/**
 * Comment Service
 * Handles all comment-related API calls
 */

/**
 * Get all comments for an issue
 * @param {string} issueId - Issue ID
 * @param {number} skip - Pagination offset
 * @param {number} limit - Pagination limit
 * @returns {Promise} Comments list with pagination info
 */
export const getComments = async (issueId, skip = 0, limit = 50) => {
  const response = await client.get(`/issues/${issueId}/comments`, {
    params: { skip, limit }
  })
  return response.data
}

/**
 * Create a new comment on an issue
 * @param {string} issueId - Issue ID
 * @param {string} content - Comment content (1-2000 characters)
 * @returns {Promise} Created comment
 */
export const createComment = async (issueId, content) => {
  const response = await client.post(`/issues/${issueId}/comments`, {
    content
  })
  return response.data
}

/**
 * Update an existing comment
 * @param {string} commentId - Comment ID
 * @param {string} content - Updated comment content
 * @returns {Promise} Updated comment
 */
export const updateComment = async (commentId, content) => {
  const response = await client.put(`/issues/comments/${commentId}`, {
    content
  })
  return response.data
}

/**
 * Delete a comment
 * @param {string} commentId - Comment ID
 * @returns {Promise}
 */
export const deleteComment = async (commentId) => {
  const response = await client.delete(`/issues/comments/${commentId}`)
  return response.data
}
