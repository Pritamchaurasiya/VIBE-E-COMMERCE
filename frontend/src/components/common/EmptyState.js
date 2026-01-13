import React from 'react';
import PropTypes from 'prop-types';
import { Box, Typography } from '@mui/material';
import { SearchOff } from '@mui/icons-material';

const EmptyState = ({ title, description, action, icon: Icon = SearchOff }) => {
  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        py: 8,
        px: 2,
        textAlign: 'center',
        backgroundColor: 'background.paper',
        borderRadius: 2,
        border: '1px dashed',
        borderColor: 'divider',
        width: '100%',
        minHeight: 300,
      }}
      role="region"
      aria-label={title}
    >
      {Icon && (
        <Icon
          sx={{
            fontSize: 64,
            color: 'text.secondary',
            mb: 2,
            opacity: 0.5
          }}
          aria-hidden="true"
        />
      )}
      <Typography
        variant="h6"
        color="text.primary"
        gutterBottom
        fontWeight="600"
      >
        {title}
      </Typography>
      {description && (
        <Typography
          variant="body2"
          color="text.secondary"
          sx={{ maxWidth: 400, mb: 3 }}
        >
          {description}
        </Typography>
      )}
      {action && (
        <Box sx={{ mt: 1 }}>
          {action}
        </Box>
      )}
    </Box>
  );
};

EmptyState.propTypes = {
  title: PropTypes.string.isRequired,
  description: PropTypes.string,
  action: PropTypes.node,
  icon: PropTypes.elementType,
};

export default EmptyState;
