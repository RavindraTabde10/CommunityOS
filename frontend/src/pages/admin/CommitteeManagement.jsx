import React, { useState, useEffect } from 'react';
import {
  Container,
  Paper,
  Typography,
  Button,
  Box,
  Snackbar,
  Alert
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import GroupsIcon from '@mui/icons-material/Groups';
import CommitteeMemberTable from '../../components/admin/CommitteeMemberTable';
import CommitteeMemberDialog from '../../components/admin/CommitteeMemberDialog';
import DeleteConfirmDialog from '../../components/admin/DeleteConfirmDialog';
import committeeService from '../../api/committeeService';

const CommitteeManagement = () => {
  const [members, setMembers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [dialogMode, setDialogMode] = useState('create');
  const [selectedMember, setSelectedMember] = useState(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [memberToDelete, setMemberToDelete] = useState(null);
  const [deleteLoading, setDeleteLoading] = useState(false);
  
  // Snackbar state
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'success'
  });

  // Load members on mount
  useEffect(() => {
    loadMembers();
  }, []);

  const loadMembers = async () => {
    setLoading(true);
    try {
      const data = await committeeService.getAllMembers();
      setMembers(data || []);
    } catch (error) {
      console.error('Failed to load committee members:', error);
      showSnackbar('Failed to load committee members', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = () => {
    setDialogMode('create');
    setSelectedMember(null);
    setDialogOpen(true);
  };

  const handleEdit = (member) => {
    setDialogMode('edit');
    setSelectedMember(member);
    setDialogOpen(true);
  };

  const handleDelete = (member) => {
    setMemberToDelete(member);
    setDeleteDialogOpen(true);
  };

  const handleSave = async (formData) => {
    try {
      if (dialogMode === 'create') {
        await committeeService.createMember(formData);
        showSnackbar('Committee member added successfully', 'success');
      } else {
        await committeeService.updateMember(selectedMember.id, formData);
        showSnackbar('Committee member updated successfully', 'success');
      }
      setDialogOpen(false);
      loadMembers(); // Reload the list
    } catch (error) {
      console.error('Failed to save committee member:', error);
      throw error; // Re-throw to let dialog handle the error
    }
  };

  const handleConfirmDelete = async () => {
    setDeleteLoading(true);
    try {
      await committeeService.deleteMember(memberToDelete.id);
      showSnackbar('Committee member removed successfully', 'success');
      setDeleteDialogOpen(false);
      setMemberToDelete(null);
      loadMembers(); // Reload the list
    } catch (error) {
      console.error('Failed to delete committee member:', error);
      showSnackbar('Failed to delete committee member', 'error');
    } finally {
      setDeleteLoading(false);
    }
  };

  const showSnackbar = (message, severity = 'success') => {
    setSnackbar({
      open: true,
      message,
      severity
    });
  };

  const handleCloseSnackbar = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      {/* Page Header */}
      <Paper sx={{ p: 3, mb: 3, bgcolor: 'primary.main', color: 'white' }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <GroupsIcon sx={{ fontSize: 40 }} />
            <Box>
              <Typography variant="h4" component="h1" fontWeight="bold">
                Committee Management
              </Typography>
              <Typography variant="body2" sx={{ mt: 0.5, opacity: 0.9 }}>
                Manage society committee members and their roles
              </Typography>
            </Box>
          </Box>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={handleCreate}
            sx={{
              bgcolor: 'white',
              color: 'primary.main',
              '&:hover': {
                bgcolor: 'grey.100'
              }
            }}
          >
            Add Member
          </Button>
        </Box>
      </Paper>

      {/* Committee Members Table */}
      <CommitteeMemberTable
        members={members}
        onEdit={handleEdit}
        onDelete={handleDelete}
        loading={loading}
      />

      {/* Create/Edit Dialog */}
      <CommitteeMemberDialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        member={selectedMember}
        onSave={handleSave}
        mode={dialogMode}
      />

      {/* Delete Confirmation Dialog */}
      <DeleteConfirmDialog
        open={deleteDialogOpen}
        onClose={() => setDeleteDialogOpen(false)}
        onConfirm={handleConfirmDelete}
        memberName={memberToDelete?.user?.full_name || 'this member'}
        loading={deleteLoading}
      />

      {/* Success/Error Snackbar */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert onClose={handleCloseSnackbar} severity={snackbar.severity} sx={{ width: '100%' }}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Container>
  );
};

export default CommitteeManagement;
