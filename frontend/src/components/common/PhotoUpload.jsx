import { useState } from 'react'
import { 
  Box, 
  Button, 
  Typography, 
  IconButton,
  Paper,
  Grid,
  ImageList,
  ImageListItem,
  ImageListItemBar
} from '@mui/material'
import CloudUploadIcon from '@mui/icons-material/CloudUpload'
import DeleteIcon from '@mui/icons-material/Delete'
import ImageIcon from '@mui/icons-material/Image'
import PropTypes from 'prop-types'

/**
 * PhotoUpload Component
 * Handles photo uploads with preview and validation
 */
const PhotoUpload = ({ photos, onPhotosChange, maxFiles = 10, maxSizeMB = 5 }) => {
  const [error, setError] = useState(null)

  const handleFileSelect = (event) => {
    const files = Array.from(event.target.files)
    setError(null)

    // Validation
    const totalFiles = photos.length + files.length
    if (totalFiles > maxFiles) {
      setError(`Maximum ${maxFiles} photos allowed`)
      return
    }

    const maxSizeBytes = maxSizeMB * 1024 * 1024
    const invalidFiles = files.filter(file => file.size > maxSizeBytes)
    if (invalidFiles.length > 0) {
      setError(`Each file must be under ${maxSizeMB}MB`)
      return
    }

    const invalidTypes = files.filter(file => !file.type.startsWith('image/'))
    if (invalidTypes.length > 0) {
      setError('Only image files are allowed')
      return
    }

    // Create preview URLs and add to photos
    const newPhotos = files.map(file => ({
      file,
      preview: URL.createObjectURL(file),
      name: file.name,
    }))

    onPhotosChange([...photos, ...newPhotos])
  }

  const handleRemovePhoto = (index) => {
    const newPhotos = photos.filter((_, i) => i !== index)
    // Revoke object URL to prevent memory leaks
    if (photos[index].preview) {
      URL.revokeObjectURL(photos[index].preview)
    }
    onPhotosChange(newPhotos)
  }

  return (
    <Box>
      <Typography variant="subtitle2" gutterBottom>
        Photos (Optional)
      </Typography>
      <Typography variant="caption" color="text.secondary" display="block" gutterBottom>
        Maximum {maxFiles} photos, {maxSizeMB}MB each
      </Typography>

      {/* Upload Button */}
      <Button
        component="label"
        variant="outlined"
        startIcon={<CloudUploadIcon />}
        disabled={photos.length >= maxFiles}
        sx={{ mt: 1, mb: 2 }}
      >
        Upload Photos
        <input
          type="file"
          hidden
          multiple
          accept="image/*"
          onChange={handleFileSelect}
        />
      </Button>

      {/* Error Message */}
      {error && (
        <Typography variant="body2" color="error" sx={{ mb: 2 }}>
          {error}
        </Typography>
      )}

      {/* Photo Preview Grid */}
      {photos.length > 0 && (
        <ImageList sx={{ width: '100%', maxHeight: 300 }} cols={3} gap={8}>
          {photos.map((photo, index) => (
            <ImageListItem key={index}>
              <img
                src={photo.preview}
                alt={photo.name}
                loading="lazy"
                style={{ height: 120, objectFit: 'cover' }}
              />
              <ImageListItemBar
                sx={{ background: 'rgba(0, 0, 0, 0.7)' }}
                title={photo.name}
                actionIcon={
                  <IconButton
                    sx={{ color: 'white' }}
                    onClick={() => handleRemovePhoto(index)}
                  >
                    <DeleteIcon />
                  </IconButton>
                }
              />
            </ImageListItem>
          ))}
        </ImageList>
      )}

      {/* Empty State */}
      {photos.length === 0 && (
        <Paper
          variant="outlined"
          sx={{
            p: 3,
            textAlign: 'center',
            bgcolor: 'grey.50',
            borderStyle: 'dashed',
          }}
        >
          <ImageIcon sx={{ fontSize: 48, color: 'grey.400', mb: 1 }} />
          <Typography variant="body2" color="text.secondary">
            No photos uploaded yet
          </Typography>
        </Paper>
      )}
    </Box>
  )
}

PhotoUpload.propTypes = {
  photos: PropTypes.array.isRequired,
  onPhotosChange: PropTypes.func.isRequired,
  maxFiles: PropTypes.number,
  maxSizeMB: PropTypes.number,
}

export default PhotoUpload
