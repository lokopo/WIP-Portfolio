import React from 'react';
import {
  Card,
  CardContent,
  CardActions,
  Typography,
  Chip,
  IconButton,
  Box,
  Stack,
  Divider
} from '@mui/material';
import {
  Edit as EditIcon,
  Delete as DeleteIcon,
  Visibility as ViewIcon,
  Business as BusinessIcon,
  LocationOn as LocationIcon,
  Schedule as ScheduleIcon,
  AttachFile as AttachFileIcon
} from '@mui/icons-material';
import { format } from 'date-fns';
import { JobApplication, ApplicationStatus } from '../types';

interface JobApplicationCardProps {
  application: JobApplication;
  onEdit: () => void;
  onDelete: () => void;
  onView: () => void;
}

const JobApplicationCard: React.FC<JobApplicationCardProps> = ({
  application,
  onEdit,
  onDelete,
  onView
}) => {
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
    <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <CardContent sx={{ flexGrow: 1 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
          <Box sx={{ flexGrow: 1 }}>
            <Typography variant="h6" component="h3" gutterBottom noWrap>
              {application.position}
            </Typography>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              <BusinessIcon sx={{ fontSize: 16, mr: 0.5, verticalAlign: 'middle' }} />
              {application.company}
            </Typography>
          </Box>
          <Chip
            label={application.status}
            color={getStatusColor(application.status) as any}
            size="small"
          />
        </Box>

        <Stack spacing={1} sx={{ mb: 2 }}>
          {application.location && (
            <Typography variant="body2" color="text.secondary">
              <LocationIcon sx={{ fontSize: 16, mr: 0.5, verticalAlign: 'middle' }} />
              {application.location}
            </Typography>
          )}
          {application.salary && (
            <Typography variant="body2" color="text.secondary">
              💰 {application.salary}
            </Typography>
          )}
          <Typography variant="body2" color="text.secondary">
            <ScheduleIcon sx={{ fontSize: 16, mr: 0.5, verticalAlign: 'middle' }} />
            Applied: {format(application.applicationDate, 'MMM dd, yyyy')}
          </Typography>
        </Stack>

        {application.jobDescription && (
          <Box sx={{ mb: 2 }}>
            <Typography variant="body2" color="text.secondary" sx={{
              display: '-webkit-box',
              WebkitLineClamp: 3,
              WebkitBoxOrient: 'vertical',
              overflow: 'hidden',
              textOverflow: 'ellipsis'
            }}>
              {application.jobDescription}
            </Typography>
          </Box>
        )}

        <Divider sx={{ my: 1 }} />

        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
          <AttachFileIcon sx={{ fontSize: 16, color: 'text.secondary' }} />
          <Typography variant="body2" color="text.secondary">
            {application.documents.length} document{application.documents.length !== 1 ? 's' : ''}
          </Typography>
        </Box>

        {application.notes && (
          <Typography variant="body2" color="text.secondary" sx={{
            display: '-webkit-box',
            WebkitLineClamp: 2,
            WebkitBoxOrient: 'vertical',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            fontStyle: 'italic'
          }}>
            📝 {application.notes}
          </Typography>
        )}
      </CardContent>

      <CardActions sx={{ justifyContent: 'space-between', px: 2, pb: 2 }}>
        <Box>
          <IconButton size="small" onClick={onView} color="primary">
            <ViewIcon />
          </IconButton>
          <IconButton size="small" onClick={onEdit} color="secondary">
            <EditIcon />
          </IconButton>
        </Box>
        <IconButton size="small" onClick={onDelete} color="error">
          <DeleteIcon />
        </IconButton>
      </CardActions>
    </Card>
  );
};

export default JobApplicationCard;