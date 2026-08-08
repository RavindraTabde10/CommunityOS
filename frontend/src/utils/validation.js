// Validation utilities and schemas
import { z } from 'zod'

// Unit number: one letter + one digit + hyphen + 4 digits, e.g. B6-1001
export const UNIT_NUMBER_REGEX = /^[A-Za-z]\d-\d{4}$/
export const UNIT_NUMBER_MSG = 'Enter a valid unit number (e.g. B6-1001 or B7-0101)'

// Email validation
export const emailSchema = z
  .string()
  .min(1, 'Email is required')
  .email('Invalid email address')

// Password validation
export const passwordSchema = z
  .string()
  .min(8, 'Password must be at least 8 characters')
  .regex(/[a-z]/, 'Password must contain at least one lowercase letter')
  .regex(/[A-Z]/, 'Password must contain at least one uppercase letter')
  .regex(/[0-9]/, 'Password must contain at least one number')

// Name validation
export const nameSchema = z
  .string()
  .min(2, 'Name must be at least 2 characters')
  .max(100, 'Name must not exceed 100 characters')

// Phone validation (optional)
export const phoneSchema = z
  .string()
  .regex(/^[0-9]{10}$/, 'Phone number must be 10 digits')
  .optional()
  .or(z.literal(''))

// Login schema
export const loginSchema = z.object({
  email: emailSchema,
  password: z.string().min(1, 'Password is required'),
})

// Register schema
export const registerSchema = z.object({
  name: nameSchema,
  email: emailSchema,
  password: passwordSchema,
  role: z.enum(['resident', 'contractor', 'builder'], {
    required_error: 'Please select a role',
  }),
  phone: phoneSchema,
  unit_number: z
    .string()
    .min(1, 'Flat number is required')
    .regex(UNIT_NUMBER_REGEX, UNIT_NUMBER_MSG),
})

// Forgot password schema
export const forgotPasswordSchema = z.object({
  email: emailSchema,
})

// Reset password schema
export const resetPasswordSchema = z.object({
  password: passwordSchema,
  confirmPassword: z.string(),
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ['confirmPassword'],
})

// Change password schema
export const changePasswordSchema = z.object({
  currentPassword: z.string().min(1, 'Current password is required'),
  newPassword: passwordSchema,
  confirmPassword: z.string(),
}).refine((data) => data.newPassword === data.confirmPassword, {
  message: "Passwords don't match",
  path: ['confirmPassword'],
})
