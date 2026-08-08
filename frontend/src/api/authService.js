import apiClient from './client'
import { API_ROUTES, STORAGE_KEYS } from '../utils/constants'

/**
 * Authentication service
 */
class AuthService {
  /**
   * Login user
   * @param {string} email 
   * @param {string} password 
   * @returns {Promise} User and token data
   */
  async login(email, password) {
    const formData = new FormData()
    formData.append('username', email)
    formData.append('password', password)

    const response = await apiClient.post(API_ROUTES.AUTH.LOGIN, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })

    // Store tokens
    if (response.data.access_token) {
      this.setTokens(response.data.access_token)
    }

    return response.data
  }

  /**
   * Register new user
   * @param {Object} userData - User registration data
   * @returns {Promise} Created user data
   */
  async register(userData) {
    const response = await apiClient.post(API_ROUTES.AUTH.REGISTER, userData)
    return response.data
  }

  /**
   * Get current user
   * @returns {Promise} Current user data
   */
  async getCurrentUser() {
    const response = await apiClient.get(API_ROUTES.AUTH.ME)
    return response.data
  }

  /**
   * Forgot password
   * @param {string} email 
   * @returns {Promise} Response message
   */
  async forgotPassword(email) {
    const response = await apiClient.post(API_ROUTES.AUTH.FORGOT_PASSWORD, { email })
    return response.data
  }

  /**
   * Reset password
   * @param {string} token 
   * @param {string} newPassword 
   * @returns {Promise} Response message
   */
  async resetPassword(token, newPassword) {
    const response = await apiClient.post(API_ROUTES.AUTH.RESET_PASSWORD, {
      token,
      new_password: newPassword,
    })
    return response.data
  }

  /**
   * Logout user
   */
  logout() {
    this.clearTokens()
  }

  /**
   * Store authentication tokens
   * @param {string} accessToken 
   */
  setTokens(accessToken) {
    localStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, accessToken)
  }

  /**
   * Get access token
   * @returns {string|null} Access token
   */
  getAccessToken() {
    return localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN)
  }

  /**
   * Clear all tokens
   */
  clearTokens() {
    localStorage.removeItem(STORAGE_KEYS.ACCESS_TOKEN)
    localStorage.removeItem(STORAGE_KEYS.USER)
  }

  /**
   * Check if user is authenticated
   * @returns {boolean}
   */
  isAuthenticated() {
    return !!this.getAccessToken()
  }
}

export default new AuthService()
