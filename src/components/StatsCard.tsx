import React from 'react';
import { Card, CardContent, Typography, Box, SxProps } from '@mui/material';
import { SvgIconProps } from '@mui/material/SvgIcon';

interface StatsCardProps {
  title: string;
  value: string | number;
  icon: React.ReactElement<SvgIconProps>;
  color?: 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning' | 'default';
  sx?: SxProps;
}

const StatsCard: React.FC<StatsCardProps> = ({ title, value, icon, color = 'primary', sx }) => {
  return (
    <Card sx={{ height: '100%', ...sx }}>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box>
            <Typography variant="h4" component="div" color={`${color}.main`} gutterBottom>
              {value}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {title}
            </Typography>
          </Box>
          <Box sx={{ color: `${color}.main` }}>
            {React.cloneElement(icon, { sx: { fontSize: 40 } })}
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
};

export default StatsCard;