import { z } from 'zod'

/**
 * Comment validation schema
 */
export const commentSchema = z.object({
  content: z
    .string()
    .min(1, 'Comment cannot be empty')
    .max(2000, 'Comment must be less than 2000 characters')
    .trim()
})

/**
 * Validate comment data
 * @param {object} data - Comment data to validate
 * @returns {object} Validation result with success flag and data/errors
 */
export const validateComment = (data) => {
  try {
    const validData = commentSchema.parse(data)
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
