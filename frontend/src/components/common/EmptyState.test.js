import React from 'react';
import { render, screen } from '@testing-library/react';
import EmptyState from './EmptyState';
import { Button } from '@mui/material';

describe('EmptyState Component', () => {
  test('renders title and description', () => {
    render(
      <EmptyState
        title="Test Title"
        description="Test Description"
      />
    );

    expect(screen.getByText('Test Title')).toBeInTheDocument();
    expect(screen.getByText('Test Description')).toBeInTheDocument();
  });

  test('renders action button when provided', () => {
    render(
      <EmptyState
        title="Test Title"
        action={<Button>Test Action</Button>}
      />
    );

    expect(screen.getByRole('button', { name: /test action/i })).toBeInTheDocument();
  });

  test('renders with default icon', () => {
    const { container } = render(<EmptyState title="Test Title" />);
    expect(container.querySelector('svg')).toBeInTheDocument();
  });
});
