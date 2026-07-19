import React from 'react';
import { render } from '@testing-library/react';
import Skeleton from '../../components/Skeleton';

describe('Skeleton component', () => {
  it('renders correctly with default classes', () => {
    const { container } = render(<Skeleton data-testid="skeleton" />);
    const skeletonElement = container.querySelector('[data-testid="skeleton"]');
    
    expect(skeletonElement).toBeInTheDocument();
    expect(skeletonElement).toHaveClass('animate-pulse', 'bg-zinc-200', 'rounded-md');
  });

  it('merges custom className prop', () => {
    const { container } = render(<Skeleton data-testid="skeleton" className="h-4 w-full" />);
    const skeletonElement = container.querySelector('[data-testid="skeleton"]');
    
    expect(skeletonElement).toHaveClass('animate-pulse', 'bg-zinc-200', 'rounded-md', 'h-4', 'w-full');
  });
});
