import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Paper,
  Container,
  Chip,
  IconButton,
  Fab,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Stack,
  Divider,
  Alert
} from '@mui/material';
import {
  Add as AddIcon,
  Work as WorkIcon,
  Schedule as ScheduleIcon,
  CheckCircle as CheckCircleIcon,
  TrendingUp as TrendingUpIcon,
  Business as BusinessIcon,
  LocationOn as LocationIcon,
  AttachFile as AttachFileIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Visibility as ViewIcon
} from '@mui/icons-material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { JobApplication, ApplicationStatus, DashboardStats } from '../types';
import JobApplicationForm from './JobApplicationForm';
import JobApplicationCard from './JobApplicationCard';
import StatsCard from './StatsCard';

const Dashboard: React.FC = () => {
  const [applications, setApplications] = useState<JobApplication[]>([]);
  const [stats, setStats] = useState<DashboardStats>({
    totalApplications: 0,
    activeApplications: 0,
    interviewsScheduled: 0,
    offersReceived: 0,
    applicationsThisMonth: 0,
    averageResponseTime: 0
  });
  const [openForm, setOpenForm] = useState(false);
  const [selectedApplication, setSelectedApplication] = useState<JobApplication | null>(null);
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState('');

  // Load applications from localStorage on component mount
  useEffect(() => {
    const savedApplications = localStorage.getItem('jobApplications');
    if (savedApplications) {
      const parsed = JSON.parse(savedApplications).map((app: any) => ({
        ...app,
        applicationDate: new Date(app.applicationDate),
        followUpDate: app.followUpDate ? new Date(app.followUpDate) : undefined,
        interviewDate: app.interviewDate ? new Date(app.interviewDate) : undefined,
        createdAt: new Date(app.createdAt),
        updatedAt: new Date(app.updatedAt)
      }));
      setApplications(parsed);
    }
  }, []);

  // Calculate stats whenever applications change
  useEffect(() => {
    const totalApplications = applications.length;
    const activeApplications = applications.filter(app => 
      [ApplicationStatus.APPLIED, ApplicationStatus.UNDER_REVIEW, ApplicationStatus.INTERVIEW_SCHEDULED, ApplicationStatus.INTERVIEWED].includes(app.status)
    ).length;
    const interviewsScheduled = applications.filter(app => 
      app.status === ApplicationStatus.INTERVIEW_SCHEDULED
    ).length;
    const offersReceived = applications.filter(app => 
      [ApplicationStatus.OFFER_RECEIVED, ApplicationStatus.OFFER_ACCEPTED].includes(app.status)
    ).length;
    
    const thisMonth = new Date().getMonth();
    const applicationsThisMonth = applications.filter(app => 
      app.applicationDate.getMonth() === thisMonth
    ).length;

    setStats({
      totalApplications,
      activeApplications,
      interviewsScheduled,
      offersReceived,
      applicationsThisMonth,
      averageResponseTime: 0 // TODO: Calculate average response time
    });
  }, [applications]);

  const saveApplications = (newApplications: JobApplication[]) => {
    setApplications(newApplications);
    localStorage.setItem('jobApplications', JSON.stringify(newApplications));
  };

  const handleAddApplication = (application: JobApplication) => {
    const newApplications = [...applications, application];
    saveApplications(newApplications);
    setOpenForm(false);
  };

  const handleUpdateApplication = (updatedApplication: JobApplication) => {
    const newApplications = applications.map(app => 
      app.id === updatedApplication.id ? updatedApplication : app
    );
    saveApplications(newApplications);
    setOpenForm(false);
    setSelectedApplication(null);
  };

  const handleDeleteApplication = (id: string) => {
    const newApplications = applications.filter(app => app.id !== id);
    saveApplications(newApplications);
  };

  const filteredApplications = applications.filter(app => {
    const matchesStatus = filterStatus === 'all' || app.status === filterStatus;
    const matchesSearch = 
      app.company.toLowerCase().includes(searchTerm.toLowerCase()) ||
      app.position.toLowerCase().includes(searchTerm.toLowerCase()) ||
      app.location?.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesStatus && matchesSearch;
  });

  const getStatusColor = (status: ApplicationStatus) => {
    switch (status) {
      case ApplicationStatus.APPLIED:
        return 'primary';
      case ApplicationStatus.UNDER_REVIEW:
        return 'info';
      case ApplicationStatus.INTERVIEW_SCHEDULED:
        return 'warning';
      case ApplicationStatus.INTERVIEWED:
        return 'secondary';
      case ApplicationStatus.OFFER_RECEIVED:
        return 'success';
      case ApplicationStatus.OFFER_ACCEPTED:
        return 'success';
      case ApplicationStatus.REJECTED:
        return 'error';
      case ApplicationStatus.WITHDRAWN:
        return 'default';
      case ApplicationStatus.NO_RESPONSE:
        return 'default';
      default:
        return 'default';
    }
  };

  return (
    <LocalizationProvider dateAdapter={AdapterDateFns}>
      <Container maxWidth="xl" sx={{ py: 4 }}>
        {/* Header */}
        <Box sx={{ mb: 4 }}>
          <Typography variant="h3" component="h1" gutterBottom>
            Job Application Tracker
          </Typography>
          <Typography variant="subtitle1" color="text.secondary">
            Keep track of your job applications, resumes, and cover letters
          </Typography>
        </Box>

        {/* Stats Cards */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6} md={2}>
            <StatsCard
              title="Total Applications"
              value={stats.totalApplications}
              icon={<WorkIcon />}
              color="primary"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={2}>
            <StatsCard
              title="Active"
              value={stats.activeApplications}
              icon={<TrendingUpIcon />}
              color="info"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={2}>
            <StatsCard
              title="Interviews"
              value={stats.interviewsScheduled}
              icon={<ScheduleIcon />}
              color="warning"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={2}>
            <StatsCard
              title="Offers"
              value={stats.offersReceived}
              icon={<CheckCircleIcon />}
              color="success"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={2}>
            <StatsCard
              title="This Month"
              value={stats.applicationsThisMonth}
              icon={<BusinessIcon />}
              color="secondary"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={2}>
            <StatsCard
              title="Avg Response"
              value={`${stats.averageResponseTime}d`}
              icon={<ScheduleIcon />}
              color="default"
            />
          </Grid>
        </Grid>

        {/* Filters and Search */}
        <Paper sx={{ p: 3, mb: 4 }}>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="Search applications..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                size="small"
              />
            </Grid>
            <Grid item xs={12} md={3}>
              <FormControl fullWidth size="small">
                <InputLabel>Filter by Status</InputLabel>
                <Select
                  value={filterStatus}
                  label="Filter by Status"
                  onChange={(e) => setFilterStatus(e.target.value)}
                >
                  <MenuItem value="all">All Statuses</MenuItem>
                  {Object.values(ApplicationStatus).map((status) => (
                    <MenuItem key={status} value={status}>
                      <Chip 
                        label={status} 
                        size="small" 
                        color={getStatusColor(status) as any}
                        sx={{ mr: 1 }}
                      />
                      {status}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={5}>
              <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
                <Button
                  variant="contained"
                  startIcon={<AddIcon />}
                  onClick={() => setOpenForm(true)}
                  size="large"
                >
                  Add New Application
                </Button>
              </Box>
            </Grid>
          </Grid>
        </Paper>

        {/* Applications Grid */}
        {filteredApplications.length === 0 ? (
          <Paper sx={{ p: 8, textAlign: 'center' }}>
            <WorkIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h6" color="text.secondary" gutterBottom>
              No applications found
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              {applications.length === 0 
                ? "Start tracking your job applications by adding your first one!"
                : "Try adjusting your search or filter criteria."
              }
            </Typography>
            {applications.length === 0 && (
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={() => setOpenForm(true)}
                size="large"
              >
                Add Your First Application
              </Button>
            )}
          </Paper>
        ) : (
          <Grid container spacing={3}>
            {filteredApplications.map((application) => (
              <Grid item xs={12} md={6} lg={4} key={application.id}>
                <JobApplicationCard
                  application={application}
                  onEdit={() => {
                    setSelectedApplication(application);
                    setOpenForm(true);
                  }}
                  onDelete={() => handleDeleteApplication(application.id)}
                  onView={() => {
                    setSelectedApplication(application);
                    setOpenForm(true);
                  }}
                />
              </Grid>
            ))}
          </Grid>
        )}

        {/* Add/Edit Application Dialog */}
        <Dialog 
          open={openForm} 
          onClose={() => {
            setOpenForm(false);
            setSelectedApplication(null);
          }}
          maxWidth="md"
          fullWidth
        >
          <JobApplicationForm
            application={selectedApplication}
            onSubmit={selectedApplication ? handleUpdateApplication : handleAddApplication}
            onCancel={() => {
              setOpenForm(false);
              setSelectedApplication(null);
            }}
          />
        </Dialog>

        {/* Floating Action Button */}
        <Fab
          color="primary"
          aria-label="add"
          sx={{ position: 'fixed', bottom: 16, right: 16 }}
          onClick={() => setOpenForm(true)}
        >
          <AddIcon />
        </Fab>
      </Container>
    </LocalizationProvider>
  );
};

export default Dashboard;