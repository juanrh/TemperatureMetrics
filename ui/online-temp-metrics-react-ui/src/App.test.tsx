import React from 'react';
import { render, screen } from '@testing-library/react';
import App from './App';

test('renders main title', () => {
  render(<App />);
  const linkElement = screen.getByText(/Temperature/i);
  expect(linkElement).toBeInTheDocument();
});
