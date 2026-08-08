import { z } from 'zod'
import { UNIT_NUMBER_REGEX, UNIT_NUMBER_MSG } from '../utils/validation'

/**
 * Profile update validation schema
 */
export const profileUpdateSchema = z.object({
  name: z
    .string()
    .min(2, 'Name must be at least 2 characters')
    .max(100, 'Name must be less than 100 characters'),
  phone: z
    .string()
    .regex(/^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$/, 'Invalid phone number format')
    .optional()
    .or(z.literal('')),
  unit_number: z
    .string()
    .regex(UNIT_NUMBER_REGEX, UNIT_NUMBER_MSG)
    .optional()
    .or(z.literal('')),
  residency_type: z
    .enum(['owner', 'tenant', ''])
    .optional()
})

/**
 * Change password validation schema
 */
export const changePasswordSchema = z.object({
  current_password: z
    .string()
    .min(1, 'Current password is required'),
  new_password: z
    .string()
    .min(8, 'Password must be at least 8 characters')
    .regex(/[A-Z]/, 'Must contain at least one uppercase letter')
    .regex(/[a-z]/, 'Must contain at least one lowercase letter')
    .regex(/[0-9]/, 'Must contain at least one number'),
  confirm_password: z.string()
}).refine((data) => data.new_password === data.confirm_password, {
  message: "Passwords don't match",
  path: ['confirm_password']
})

/**
 * Validate profile update data
 */
export const validateProfileUpdate = (data) => {
  try {
    const validData = profileUpdateSchema.parse(data)
    return { success: true, data: validData }
  } catch (error) {
    return {
      success: false,
      errors: error.errors.reduce((acc, err) => {
        acc[err.path[0]] = err.message
        return acc
      }, {})
    }
  }
}

/**
 * Validate password change data
 */
export const validatePasswordChange = (data) => {
  try {
    const validData = changePasswordSchema.parse(data)
    return { success: true, data: validData }
  } catch (error) {
    return {
      success: false,
      errors: error.errors.reduce((acc, err) => {
        acc[err.path[0]] = err.message
        return acc
      }, {})
    }
  }
}
