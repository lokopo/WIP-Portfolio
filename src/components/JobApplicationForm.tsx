import React, { useState, useEffect } from 'react';
import {
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  Box,
  Typography,
  Chip,
  IconButton,
  Stack,
  Divider,
  Alert,
  FormHelperText
} from '@mui/material';
import {
  Close as CloseIcon,
  Add as AddIcon,
  Delete as DeleteIcon,
  AttachFile as AttachFileIcon
} from '@mui/icons-material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { v4 as uuidv4 } from 'uuid';
import { JobApplication, ApplicationStatus, DocumentType, Resume, CoverLetter, Document } from '../types';

interface JobApplicationFormProps {
  application?: JobApplication | null;
  onSubmit: (application: JobApplication) => void;
  onCancel: () => void;
}

const JobApplicationForm: React.FC<JobApplicationFormProps> = ({
  application,
  onSubmit,
  onCancel
}) => {
  const [formData, setFormData] = useState<Partial<JobApplication>>({
    company: '',
    position: '',
    jobDescription: '',
    applicationDate: new Date(),
    status: ApplicationStatus.APPLIED,
    salary: '',
    location: '',
    contactPerson: '',
    contactEmail: '',
    contactPhone: '',
    jobUrl: '',
    notes: '',
    resume: {
      id: uuidv4(),
      name: 'Default Resume',
      content: '',
      fileName: 'resume.pdf',
      createdAt: new Date()
    },
    coverLetter: undefined,
    documents: [],
    followUpDate: undefined,
    interviewDate: undefined
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    if (application) {
      setFormData(application);
    }
  }, [application]);

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.company?.trim()) {
      newErrors.company = 'Company name is required';
    }
    if (!formData.position?.trim()) {
      newErrors.position = 'Position is required';
    }
    if (!formData.jobDescription?.trim()) {
      newErrors.jobDescription = 'Job description is required';
    }
    if (!formData.applicationDate) {
      newErrors.applicationDate = 'Application date is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = () => {
    if (!validateForm()) return;

    const now = new Date();
    const applicationData: JobApplication = {
      id: application?.id || uuidv4(),
      company: formData.company!,
      position: formData.position!,
      jobDescription: formData.jobDescription!,
      applicationDate: formData.applicationDate!,
      status: formData.status!,
      salary: formData.salary,
      location: formData.location,
      contactPerson: formData.contactPerson,
      contactEmail: formData.contactEmail,
      contactPhone: formData.contactPhone,
      jobUrl: formData.jobUrl,
      notes: formData.notes,
      resume: formData.resume!,
      coverLetter: formData.coverLetter,
      documents: formData.documents || [],
      followUpDate: formData.followUpDate,
      interviewDate: formData.interviewDate,
      createdAt: application?.createdAt || now,
      updatedAt: now
    };

    onSubmit(applicationData);
  };

  const handleInputChange = (field: string, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  const handleResumeChange = (field: string, value: string) => {
    setFormData(prev => ({
      ...prev,
      resume: { ...prev.resume!, [field]: value }
    }));
  };

  const handleCoverLetterChange = (field: string, value: string) => {
    setFormData(prev => ({
      ...prev,
      coverLetter: prev.coverLetter ? { ...prev.coverLetter, [field]: value } : {
        id: uuidv4(),
        name: 'Cover Letter',
        content: '',
        fileName: 'cover-letter.pdf',
        createdAt: new Date()
      }
    }));
  };

  const addDocument = () => {
    const newDocument: Document = {
      id: uuidv4(),
      name: 'New Document',
      type: DocumentType.OTHER,
      fileName: 'document.pdf',
      createdAt: new Date()
    };
    setFormData(prev => ({
      ...prev,
      documents: [...(prev.documents || []), newDocument]
    }));
  };

  const updateDocument = (id: string, field: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      documents: prev.documents?.map(doc => 
        doc.id === id ? { ...doc, [field]: value } : doc
      )
    }));
  };

  const removeDocument = (id: string) => {
    setFormData(prev => ({
      ...prev,
      documents: prev.documents?.filter(doc => doc.id !== id)
    }));
  };

  return (
    <>
      <DialogTitle sx={{ m: 0, p: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h6">
          {application ? 'Edit Application' : 'Add New Application'}
        </Typography>
        <IconButton onClick={onCancel}>
          <CloseIcon />
        </IconButton>
      </DialogTitle>

      <DialogContent dividers sx={{ minHeight: '60vh' }}>
        <Grid container spacing={3}>
          {/* Basic Information */}
          <Grid item xs={12}>
            <Typography variant="h6" gutterBottom>
              Basic Information
            </Typography>
          </Grid>

          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Company *"
              value={formData.company || ''}
              onChange={(e) => handleInputChange('company', e.target.value)}
              error={!!errors.company}
              helperText={errors.company}
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Position *"
              value={formData.position || ''}
              onChange={(e) => handleInputChange('position', e.target.value)}
              error={!!errors.position}
              helperText={errors.position}
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Location"
              value={formData.location || ''}
              onChange={(e) => handleInputChange('location', e.target.value)}
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Salary"
              value={formData.salary || ''}
              onChange={(e) => handleInputChange('salary', e.target.value)}
              placeholder="e.g., $50,000 - $70,000"
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <DatePicker
              label="Application Date *"
              value={formData.applicationDate || null}
              onChange={(date) => handleInputChange('applicationDate', date)}
              slotProps={{
                textField: {
                  fullWidth: true,
                  error: !!errors.applicationDate,
                  helperText: errors.applicationDate
                }
              }}
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>Status *</InputLabel>
              <Select
                value={formData.status || ApplicationStatus.APPLIED}
                label="Status *"
                onChange={(e) => handleInputChange('status', e.target.value)}
              >
                {Object.values(ApplicationStatus).map((status) => (
                  <MenuItem key={status} value={status}>
                    {status}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Job URL"
              value={formData.jobUrl || ''}
              onChange={(e) => handleInputChange('jobUrl', e.target.value)}
              placeholder="https://..."
            />
          </Grid>

          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Job Description *"
              value={formData.jobDescription || ''}
              onChange={(e) => handleInputChange('jobDescription', e.target.value)}
              multiline
              rows={4}
              error={!!errors.jobDescription}
              helperText={errors.jobDescription}
            />
          </Grid>

          <Grid item xs={12}>
            <Divider sx={{ my: 2 }} />
            <Typography variant="h6" gutterBottom>
              Contact Information
            </Typography>
          </Grid>

          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              label="Contact Person"
              value={formData.contactPerson || ''}
              onChange={(e) => handleInputChange('contactPerson', e.target.value)}
            />
          </Grid>

          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              label="Contact Email"
              value={formData.contactEmail || ''}
              onChange={(e) => handleInputChange('contactEmail', e.target.value)}
              type="email"
            />
          </Grid>

          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              label="Contact Phone"
              value={formData.contactPhone || ''}
              onChange={(e) => handleInputChange('contactPhone', e.target.value)}
            />
          </Grid>

          <Grid item xs={12}>
            <Divider sx={{ my: 2 }} />
            <Typography variant="h6" gutterBottom>
              Documents
            </Typography>
          </Grid>

          {/* Resume */}
          <Grid item xs={12}>
            <Typography variant="subtitle1" gutterBottom>
              Resume
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Resume Name"
                  value={formData.resume?.name || ''}
                  onChange={(e) => handleResumeChange('name', e.target.value)}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Resume Content"
                  value={formData.resume?.content || ''}
                  onChange={(e) => handleResumeChange('content', e.target.value)}
                  multiline
                  rows={3}
                  placeholder="Paste your resume content or notes here..."
                />
              </Grid>
            </Grid>
          </Grid>

          {/* Cover Letter */}
          <Grid item xs={12}>
            <Typography variant="subtitle1" gutterBottom>
              Cover Letter (Optional)
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Cover Letter Name"
                  value={formData.coverLetter?.name || ''}
                  onChange={(e) => handleCoverLetterChange('name', e.target.value)}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Cover Letter Content"
                  value={formData.coverLetter?.content || ''}
                  onChange={(e) => handleCoverLetterChange('content', e.target.value)}
                  multiline
                  rows={3}
                  placeholder="Paste your cover letter content here..."
                />
              </Grid>
            </Grid>
          </Grid>

          {/* Additional Documents */}
          <Grid item xs={12}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="subtitle1">
                Additional Documents
              </Typography>
              <Button
                startIcon={<AddIcon />}
                onClick={addDocument}
                size="small"
              >
                Add Document
              </Button>
            </Box>

            <Stack spacing={2}>
              {formData.documents?.map((doc, index) => (
                <Box key={doc.id} sx={{ p: 2, border: '1px solid', borderColor: 'divider', borderRadius: 1 }}>
                  <Grid container spacing={2} alignItems="center">
                    <Grid item xs={12} md={3}>
                      <TextField
                        fullWidth
                        label="Document Name"
                        value={doc.name}
                        onChange={(e) => updateDocument(doc.id, 'name', e.target.value)}
                        size="small"
                      />
                    </Grid>
                    <Grid item xs={12} md={3}>
                      <FormControl fullWidth size="small">
                        <InputLabel>Type</InputLabel>
                        <Select
                          value={doc.type}
                          label="Type"
                          onChange={(e) => updateDocument(doc.id, 'type', e.target.value)}
                        >
                          {Object.values(DocumentType).map((type) => (
                            <MenuItem key={type} value={type}>
                              {type}
                            </MenuItem>
                          ))}
                        </Select>
                      </FormControl>
                    </Grid>
                    <Grid item xs={12} md={4}>
                      <TextField
                        fullWidth
                        label="Description"
                        value={doc.description || ''}
                        onChange={(e) => updateDocument(doc.id, 'description', e.target.value)}
                        size="small"
                      />
                    </Grid>
                    <Grid item xs={12} md={2}>
                      <IconButton
                        onClick={() => removeDocument(doc.id)}
                        color="error"
                        size="small"
                      >
                        <DeleteIcon />
                      </IconButton>
                    </Grid>
                  </Grid>
                </Box>
              ))}
            </Stack>
          </Grid>

          <Grid item xs={12}>
            <Divider sx={{ my: 2 }} />
            <Typography variant="h6" gutterBottom>
              Additional Information
            </Typography>
          </Grid>

          <Grid item xs={12} md={6}>
            <DatePicker
              label="Follow-up Date"
              value={formData.followUpDate || null}
              onChange={(date) => handleInputChange('followUpDate', date)}
              slotProps={{
                textField: { fullWidth: true }
              }}
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <DatePicker
              label="Interview Date"
              value={formData.interviewDate || null}
              onChange={(date) => handleInputChange('interviewDate', date)}
              slotProps={{
                textField: { fullWidth: true }
              }}
            />
          </Grid>

          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Notes"
              value={formData.notes || ''}
              onChange={(e) => handleInputChange('notes', e.target.value)}
              multiline
              rows={3}
              placeholder="Additional notes, reminders, or observations..."
            />
          </Grid>
        </Grid>
      </DialogContent>

      <DialogActions sx={{ p: 2 }}>
        <Button onClick={onCancel}>
          Cancel
        </Button>
        <Button
          onClick={handleSubmit}
          variant="contained"
          disabled={Object.keys(errors).length > 0}
        >
          {application ? 'Update Application' : 'Add Application'}
        </Button>
      </DialogActions>
    </>
  );
};

export default JobApplicationForm;