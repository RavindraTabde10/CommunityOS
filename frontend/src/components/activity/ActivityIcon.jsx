import AddCircleIcon from '@mui/icons-material/AddCircle'
import EditIcon from '@mui/icons-material/Edit'
import ChangeCircleIcon from '@mui/icons-material/ChangeCircle'
import CommentIcon from '@mui/icons-material/Comment'
import PhotoIcon from '@mui/icons-material/PhotoCamera'
import AssignmentIndIcon from '@mui/icons-material/AssignmentInd'
import DeleteIcon from '@mui/icons-material/Delete'
import UpdateIcon from '@mui/icons-material/Update'

/**
 * ActivityIcon Component
 * Returns appropriate icon for activity type
 */
const ActivityIcon = ({ activityType }) => {
  const iconMap = {
    created: <AddCircleIcon sx={{ color: 'success.main' }} />,
    updated: <EditIcon sx={{ color: 'info.main' }} />,
    status_changed: <ChangeCircleIcon sx={{ color: 'warning.main' }} />,
    commented: <CommentIcon sx={{ color: 'primary.main' }} />,
    photo_uploaded: <PhotoIcon sx={{ color: 'secondary.main' }} />,
    assigned: <AssignmentIndIcon sx={{ color: 'info.main' }} />,
    deleted: <DeleteIcon sx={{ color: 'error.main' }} />,
  }

  // Default icon if type not found
  return iconMap[activityType] || <UpdateIcon sx={{ color: 'action.active' }} />
}

export default ActivityIcon
