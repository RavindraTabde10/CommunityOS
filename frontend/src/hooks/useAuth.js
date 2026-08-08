import { useDispatch, useSelector } from 'react-redux'
import { useNavigate } from 'react-router-dom'
import {
  login as loginAction,
  register as registerAction,
  logout as logoutAction,
  getCurrentUser,
  selectUser,
  selectIsAuthenticated,
  selectAuthLoading,
  selectAuthError,
  clearError,
} from '../store/authSlice'
import { ROUTES } from '../utils/constants'

/**
 * Custom hook for authentication
 * @returns {Object} Auth state and methods
 */
export const useAuth = () => {
  const dispatch = useDispatch()
  const navigate = useNavigate()

  const user = useSelector(selectUser)
  const isAuthenticated = useSelector(selectIsAuthenticated)
  const isLoading = useSelector(selectAuthLoading)
  const error = useSelector(selectAuthError)

  /**
   * Login user
   * @param {string} email 
   * @param {string} password 
   */
  const login = async (email, password) => {
    const result = await dispatch(loginAction({ email, password }))
    if (!result.error) {
      navigate(ROUTES.DASHBOARD)
    }
    return result
  }

  /**
   * Register user
   * @param {Object} userData 
   */
  const register = async (userData) => {
    const result = await dispatch(registerAction(userData))
    if (!result.error) {
      navigate(ROUTES.LOGIN)
    }
    return result
  }

  /**
   * Logout user
   */
  const logout = async () => {
    await dispatch(logoutAction())
    navigate(ROUTES.LOGIN)
  }

  /**
   * Fetch current user
   */
  const fetchCurrentUser = async () => {
    return await dispatch(getCurrentUser())
  }

  /**
   * Clear error
   */
  const clear = () => {
    dispatch(clearError())
  }

  return {
    user,
    isAuthenticated,
    isLoading,
    error,
    login,
    register,
    logout,
    fetchCurrentUser,
    clearError: clear,
  }
}
