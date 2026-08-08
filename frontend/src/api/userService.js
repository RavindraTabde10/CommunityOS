import apiClient from './client'
import { API_ROUTES } from '../utils/constants'

/**
 * User service
 */
class UserService {
  /**
   * Get all users (admin only)
   * @param {Object} params - Query parameters
   * @returns {Promise} List of users
   */
  async getUsers(params = {}) {
    const response = await apiClient.get(API_ROUTES.USERS.BASE, { params })
    return response.data
  }

  async createUser(userData) {
    const response = await apiClient.post(API_ROUTES.USERS.BASE, userData)
    return response.data
  }

  /**
   * Get user by ID
   * @param {string} userId 
   * @returns {Promise} User data
   */
  async getUserById(userId) {
    const response = await apiClient.get(`${API_ROUTES.USERS.BASE}/${userId}`)
    return response.data
  }

  /**
   * Get current user profile
   * @returns {Promise} Current user data
   */
  async getProfile() {
    const response = await apiClient.get(API_ROUTES.USERS.ME)
    return response.data
  }

  /**
   * Update current user profile
   * @param {Object} userData - Updated user data
   * @returns {Promise} Updated user data
   */
  async updateProfile(userData) {
    const response = await apiClient.put(API_ROUTES.USERS.ME, userData)
    return response.data
  }

  /**
   * Change password
   * @param {string} currentPassword 
   * @param {string} newPassword 
   * @returns {Promise} Response message
   */
  async changePassword(currentPassword, newPassword) {
    const response = await apiClient.put(API_ROUTES.USERS.UPDATE_PASSWORD, {
      current_password: currentPassword,
      new_password: newPassword,
    })
    return response.data
  }

  /**
   * Update user (admin only)
   * @param {string} userId 
   * @param {Object} userData 
   * @returns {Promise} Updated user data
   */
  async updateUser(userId, userData) {
    const response = await apiClient.put(`${API_ROUTES.USERS.BASE}/${userId}`, userData)
    return response.data
  }

  /**
   * Delete user (admin only)
   * @param {string} userId 
   * @returns {Promise} Response message
   */
  async deleteUser(userId) {
    const response = await apiClient.delete(`${API_ROUTES.USERS.BASE}/${userId}`)
    return response.data
  }

  /**
   * Update user role (admin only)
   * @param {string} userId 
   * @param {string} role 
   * @returns {Promise} Updated user data
   */
  async updateUserRole(userId, role) {
    const response = await apiClient.patch(`${API_ROUTES.USERS.BASE}/${userId}/role`, { role })
    return response.data
  }

  /**
   * Update user status (admin only)
   * @param {string} userId 
   * @param {boolean} isActive 
   * @returns {Promise} Updated user data
   */
  async updateUserStatus(userId, isActive) {
    const response = await apiClient.patch(`${API_ROUTES.USERS.BASE}/${userId}/status`, {
      is_active: isActive,
    })
    return response.data
  }
}

export default new UserService()
