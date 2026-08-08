import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  MenuItem,
  FormControlLabel,
  Checkbox,
  Grid,
  Box,
  Alert,
  CircularProgress
} from '@mui/material';
import { COMMITTEE_ROLES_ARRAY, ROLE_LABELS } from '../../constants/committee';
import apiClient from '../../api/client';

const CommitteeMemberDialog = ({ open, onClose, member, onSave, mode = 'create' }) => {
  const [loading, setLoading] = useState(false);
  const [users, setUsers] = useState([]);
  const [error, setError] = useState('');
  const [formData, setFormData] = useState({
    user_id: '',
    role: 'member',
    position_name: '',
    responsibilities: '',
    contact_email: '',
    contact_phone: '',
    display_order: 99,
    term_start_date: '',
    term_end_date: '',
    is_active: true
  });

  // Load users on mount
  useEffect(() => {
    if (open) {
      loadUsers();
    }
  }, [open]);

  // Populate form when editing
  useEffect(() => {
    if (member && mode === 'edit') {
      setFormData({
        user_id: member.user_id || '',
        role: member.role || 'member',
        position_name: member.position_name || '',
        responsibilities: member.responsibilities || '',
        contact_email: member.contact_email || '',
        contact_phone: member.contact_phone || '',
        display_order: member.display_order || 99,
        term_start_date: member.term_start_date ? member.term_start_date.split('T')[0] : '',
        term_end_date: member.term_end_date ? member.term_end_date.split('T')[0] : '',
        is_active: member.is_active !== undefined ? member.is_active : true
      });
    } else if (mode === 'create') {
      // Reset form for create mode
      setFormData({
        user_id: '',
        role: 'member',
        position_name: '',
        responsibilities: '',
        contact_email: '',
        contact_phone: '',
        display_order: 99,
        term_start_date: '',
        term_end_date: '',
        is_active: true
      });
    }
  }, [member, mode, open]);

  const loadUsers = async () => {
    try {
      const response = await apiClient.get('/users');
      // API returns { users: [...] } format
      const usersArray = response.data?.users || response.data || [];
      setUsers(usersArray);
    } catch (err) {
      console.error('Failed to load users:', err);
      setError('Failed to load users. Please try again.');
    }
  };

  const handleChange = (e) => {
    const { name, value, checked, type } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
    setError(''); // Clear error on change
  };

  const validateForm = () => {
    if (!formData.user_id) {
      setError('Please select a user');
      return false;
    }
    if (!formData.role) {
      setError('Please select a role');
      return false;
    }
    if (!formData.position_name.trim()) {
      setError('Position name is required');
      return false;
    }
    if (formData.contact_email && !isValidEmail(formData.contact_email)) {
      setError('Invalid email format');
      return false;
    }
    if (formData.term_end_date && formData.term_start_date && 
        new Date(formData.term_end_date) < new Date(formData.term_start_date)) {
      setError('Term end date must be after start date');
      return false;
    }
    return true;
  };

  const isValidEmail = (email) => {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  };

  const handleSubmit = async () => {
    if (!validateForm()) {
      return;
    }

    setLoading(true);
    setError('');

    try {
      // Prepare data for API
      const submitData = {
        ...formData,
        user_id: formData.user_id,
        display_order: parseInt(formData.display_order) || 99,
        term_start_date: formData.term_start_date ? `${formData.term_start_date}T00:00:00` : null,
        term_end_date: formData.term_end_date ? `${formData.term_end_date}T23:59:59` : null,
        contact_email: formData.contact_email || null,
        contact_phone: formData.contact_phone || null,
        responsibilities: formData.responsibilities || null
      };

      console.log('Submitting committee member data:', submitData);
      await onSave(submitData);
      handleClose();
    } catch (err) {
      console.error('Failed to save committee member:', err);
      
      // Handle different error response formats
      let errorMessage = 'Failed to save committee member. Please try again.';
      
      if (err.response?.data?.detail) {
        const detail = err.response.data.detail;
        
        // If detail is an array (validation errors)
        if (Array.isArray(detail)) {
          errorMessage = detail.map(e => e.msg || e.message || JSON.stringify(e)).join(', ');
        } 
        // If detail is a string
        else if (typeof detail === 'string') {
          errorMessage = detail;
        }
        // If detail is an object
        else if (typeof detail === 'object') {
          errorMessage = detail.msg || detail.message || JSON.stringify(detail);
        }
      } else if (err.message) {
        errorMessage = err.message;
      }
      
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setError('');
    setFormData({
      user_id: '',
      role: 'member',
      position_name: '',
      responsibilities: '',
      contact_email: '',
      contact_phone: '',
      display_order: 99,
      term_start_date: '',
      term_end_date: '',
      is_active: true
    });
    onClose();
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
      <DialogTitle>
        {mode === 'create' ? '➕ Add Committee Member' : '✏️ Edit Committee Member'}
      </DialogTitle>
      <DialogContent>
        <Box sx={{ mt: 2 }}>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          <Grid container spacing={2}>
            {/* User Selection */}
            <Grid item xs={12}>
              <TextField
                select
                fullWidth
                label="Select User"
                name="user_id"
                value={formData.user_id}
                onChange={handleChange}
                required
                disabled={mode === 'edit'} // Can't change user when editing
              >
                <MenuItem value="">
                  <em>-- Select User --</em>
                </MenuItem>
                {users.map((user) => (
                  <MenuItem key={user.id} value={user.id}>
                    {user.full_name} ({user.email}) - Unit: {user.unit_number || 'N/A'}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>

            {/* Role Selection */}
            <Grid item xs={12} sm={6}>
              <TextField
                select
                fullWidth
                label="Role"
                name="role"
                value={formData.role}
                onChange={handleChange}
                required
              >
                {COMMITTEE_ROLES_ARRAY.map((role) => (
                  <MenuItem key={role} value={role}>
                    {ROLE_LABELS[role]}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>

            {/* Position Name */}
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Position Name"
                name="position_name"
                value={formData.position_name}
                onChange={handleChange}
                required
                placeholder="e.g., Society President"
              />
            </Grid>

            {/* Responsibilities */}
            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={3}
                label="Responsibilities"
                name="responsibilities"
                value={formData.responsibilities}
                onChange={handleChange}
                placeholder="Describe the key responsibilities..."
              />
            </Grid>

            {/* Contact Email */}
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                type="email"
                label="Contact Email"
                name="contact_email"
                value={formData.contact_email}
                onChange={handleChange}
                placeholder="president@riverdale.com"
              />
            </Grid>

            {/* Contact Phone */}
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Contact Phone"
                name="contact_phone"
                value={formData.contact_phone}
                onChange={handleChange}
                placeholder="+91-9876543210"
              />
            </Grid>

            {/* Display Order */}
            <Grid item xs={12} sm={4}>
              <TextField
                fullWidth
                type="number"
                label="Display Order"
                name="display_order"
                value={formData.display_order}
                onChange={handleChange}
                inputProps={{ min: 1, max: 999 }}
                helperText="Lower numbers appear first"
              />
            </Grid>

            {/* Term Start Date */}
            <Grid item xs={12} sm={4}>
              <TextField
                fullWidth
                type="date"
                label="Term Start Date"
                name="term_start_date"
                value={formData.term_start_date}
                onChange={handleChange}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>

            {/* Term End Date */}
            <Grid item xs={12} sm={4}>
              <TextField
                fullWidth
                type="date"
                label="Term End Date"
                name="term_end_date"
                value={formData.term_end_date}
                onChange={handleChange}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>

            {/* Active Status */}
            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Checkbox
                    name="is_active"
                    checked={formData.is_active}
                    onChange={handleChange}
                  />
                }
                label="Active (Display on dashboard)"
              />
            </Grid>
          </Grid>
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose} disabled={loading}>
          Cancel
        </Button>
        <Button
          onClick={handleSubmit}
          variant="contained"
          disabled={loading}
          startIcon={loading && <CircularProgress size={20} />}
        >
          {loading ? 'Saving...' : mode === 'create' ? 'Add Member' : 'Save Changes'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default CommitteeMemberDialog;
