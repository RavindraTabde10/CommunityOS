import React from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Avatar,
  Chip,
  IconButton,
  Tooltip,
  Box,
  Typography
} from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import EmailIcon from '@mui/icons-material/Email';
import PhoneIcon from '@mui/icons-material/Phone';
import { getRoleLabel, getRoleIcon } from '../../constants/committee';

const CommitteeMemberTable = ({ members, onEdit, onDelete, loading }) => {
  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const getTermDisplay = (startDate, endDate) => {
    if (!startDate && !endDate) return 'Indefinite';
    if (!endDate) return `From ${formatDate(startDate)}`;
    return `${formatDate(startDate)} - ${formatDate(endDate)}`;
  };

  if (loading) {
    return (
      <Box sx={{ textAlign: 'center', py: 4 }}>
        <Typography>Loading committee members...</Typography>
      </Box>
    );
  }

  if (!members || members.length === 0) {
    return (
      <Paper sx={{ p: 4, textAlign: 'center' }}>
        <Typography variant="h6" color="text.secondary">
          No committee members found
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
          Click "Add Member" to create your first committee member
        </Typography>
      </Paper>
    );
  }

  return (
    <TableContainer component={Paper}>
      <Table>
        <TableHead>
          <TableRow sx={{ bgcolor: 'primary.main' }}>
            <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Member</TableCell>
            <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Role</TableCell>
            <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Position</TableCell>
            <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Contact</TableCell>
            <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Term</TableCell>
            <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Status</TableCell>
            <TableCell sx={{ color: 'white', fontWeight: 'bold' }} align="center">
              Actions
            </TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {members.map((member) => (
            <TableRow
              key={member.id}
              sx={{
                '&:hover': { bgcolor: 'action.hover' },
                '&:nth-of-type(even)': { bgcolor: 'action.hover' }
              }}
            >
              {/* Member Info */}
              <TableCell>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <Avatar sx={{ bgcolor: 'primary.main' }}>
                    {member.user_name?.charAt(0) || 'U'}
                  </Avatar>
                  <Box>
                    <Typography variant="body1" fontWeight="bold">
                      {member.user_name || 'Unknown User'}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Unit: {member.user_unit || 'N/A'}
                    </Typography>
                  </Box>
                </Box>
              </TableCell>

              {/* Role */}
              <TableCell>
                <Chip
                  label={`${getRoleIcon(member.role)} ${getRoleLabel(member.role)}`}
                  color="primary"
                  variant="outlined"
                  size="small"
                />
              </TableCell>

              {/* Position */}
              <TableCell>
                <Typography variant="body2">{member.position_name}</Typography>
                {member.responsibilities && (
                  <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 0.5 }}>
                    {member.responsibilities.substring(0, 50)}
                    {member.responsibilities.length > 50 ? '...' : ''}
                  </Typography>
                )}
              </TableCell>

              {/* Contact */}
              <TableCell>
                <Box sx={{ display: 'flex', gap: 0.5 }}>
                  {member.contact_email && (
                    <Tooltip title={member.contact_email}>
                      <IconButton
                        size="small"
                        color="primary"
                        onClick={() => window.location.href = `mailto:${member.contact_email}`}
                      >
                        <EmailIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  )}
                  {member.contact_phone && (
                    <Tooltip title={member.contact_phone}>
                      <IconButton
                        size="small"
                        color="primary"
                        onClick={() => window.location.href = `tel:${member.contact_phone}`}
                      >
                        <PhoneIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  )}
                  {!member.contact_email && !member.contact_phone && (
                    <Typography variant="caption" color="text.secondary">
                      No contact info
                    </Typography>
                  )}
                </Box>
              </TableCell>

              {/* Term */}
              <TableCell>
                <Typography variant="caption">
                  {getTermDisplay(member.term_start_date, member.term_end_date)}
                </Typography>
              </TableCell>

              {/* Status */}
              <TableCell>
                <Chip
                  label={member.is_active ? 'Active' : 'Inactive'}
                  color={member.is_active ? 'success' : 'default'}
                  size="small"
                />
              </TableCell>

              {/* Actions */}
              <TableCell align="center">
                <Tooltip title="Edit">
                  <IconButton
                    color="primary"
                    size="small"
                    onClick={() => onEdit(member)}
                  >
                    <EditIcon />
                  </IconButton>
                </Tooltip>
                <Tooltip title="Delete">
                  <IconButton
                    color="error"
                    size="small"
                    onClick={() => onDelete(member)}
                  >
                    <DeleteIcon />
                  </IconButton>
                </Tooltip>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
};

export default CommitteeMemberTable;
