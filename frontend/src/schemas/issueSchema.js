import { z } from 'zod'

/**
 * Issue Form Validation Schema
 * Validates issue creation and update forms
 */
export const issueSchema = z.object({
  title: z
    .string()
    .min(10, 'Title must be at least 10 characters')
    .max(200, 'Title must not exceed 200 characters'),
  
  description: z
    .string()
    .min(20, 'Description must be at least 20 characters')
    .max(2000, 'Description must not exceed 2000 characters'),
  
  category: z
    .enum(['electrical', 'plumbing', 'painting', 'carpentry', 'flooring', 'civil', 'other'], {
      required_error: 'Category is required',
      invalid_type_error: 'Invalid category',
    }),
  
  priority: z
    .enum(['low', 'medium', 'high', 'critical'], {
      required_error: 'Priority is required',
      invalid_type_error: 'Invalid priority',
    }),
  
  location: z
    .string()
    .max(200, 'Location must not exceed 200 characters')
    .optional()
    .or(z.literal('')),
  
  unit_number: z
    .string()
    .regex(/^[A-Za-z]\d-\d{4}$/, 'Enter a valid unit number (e.g. B6-1001 or B7-0101)')
    .optional()
    .or(z.literal('')),

  assigned_to: z
    .string()
    .optional()
    .nullable()
    .or(z.literal('')),
})

/**
 * Category options for dropdown
 */
export const CATEGORY_OPTIONS = [
  { value: 'electrical', label: 'Electrical' },
  { value: 'plumbing', label: 'Plumbing' },
  { value: 'painting', label: 'Painting' },
  { value: 'carpentry', label: 'Carpentry' },
  { value: 'flooring', label: 'Flooring' },
  { value: 'civil', label: 'Civil' },
  { value: 'other', label: 'Other' },
]

/**
 * Priority options for dropdown
 */
export const PRIORITY_OPTIONS = [
  { value: 'low', label: 'Low', description: 'Can wait' },
  { value: 'medium', label: 'Medium', description: 'Normal priority' },
  { value: 'high', label: 'High', description: 'Needs attention' },
  { value: 'critical', label: 'Critical', description: 'Urgent!' },
]
