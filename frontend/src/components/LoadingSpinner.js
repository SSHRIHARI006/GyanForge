import React from 'react';
import { Loader2 } from 'lucide-react';

const LoadingSpinner = ({ 
  size = 'md', 
  text = 'Loading...', 
  overlay = false,
  className = '' 
}) => {
  const sizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-8 w-8',
    lg: 'h-12 w-12',
    xl: 'h-16 w-16'
  };

  const spinnerComponent = (
    <div className={`flex flex-col items-center justify-center ${className}`}>
      <Loader2 className={`${sizeClasses[size]} text-primary-500 animate-spin`} />
      {text && (
        <p className="mt-3 text-gray-300 text-sm font-medium">
          {text}
        </p>
      )}
    </div>
  );

  if (overlay) {
    return (
      <div className="fixed inset-0 bg-dark-900 bg-opacity-75 flex items-center justify-center z-50">
        <div className="bg-dark-800 rounded-lg p-8 shadow-xl">
          {spinnerComponent}
        </div>
      </div>
    );
  }

  return spinnerComponent;
};

// Page-level loading component
export const PageLoader = ({ text = 'Loading page...' }) => (
  <div className="min-h-screen bg-dark-900 flex items-center justify-center">
    <LoadingSpinner size="xl" text={text} />
  </div>
);

// Section-level loading component
export const SectionLoader = ({ text = 'Loading...', className = 'py-12' }) => (
  <div className={`flex items-center justify-center ${className}`}>
    <LoadingSpinner size="lg" text={text} />
  </div>
);

// Button loading state
export const ButtonLoader = ({ text = 'Processing...' }) => (
  <div className="flex items-center justify-center gap-2">
    <Loader2 className="h-4 w-4 animate-spin" />
    <span>{text}</span>
  </div>
);

export default LoadingSpinner;
