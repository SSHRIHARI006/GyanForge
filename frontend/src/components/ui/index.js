import React from 'react';
import clsx from 'clsx';

export const Button = ({ 
  children, 
  variant = 'primary', 
  size = 'md', 
  loading = false, 
  disabled = false,
  onClick,
  type = 'button',
  className = '',
  ...props 
}) => {
  const baseClasses = 'inline-flex items-center justify-center font-medium rounded-lg focus:outline-none focus:ring-2 focus:ring-offset-2 transition-colors duration-200';
  
  const variants = {
    primary: 'bg-primary-600 text-white hover:bg-primary-700 focus:ring-primary-500',
    secondary: 'bg-dark-600 text-white hover:bg-dark-700 focus:ring-dark-500',
    outline: 'border border-dark-600 text-gray-300 bg-dark-800 hover:bg-dark-700 focus:ring-primary-500',
    success: 'bg-success-600 text-white hover:bg-success-700 focus:ring-success-500',
    danger: 'bg-error-500 text-white hover:bg-red-600 focus:ring-red-500',
    ghost: 'text-gray-300 hover:text-gray-100 hover:bg-dark-700 focus:ring-gray-500',
  };
  
  const sizes = {
    sm: 'px-3 py-2 text-sm',
    md: 'px-4 py-2 text-sm',
    lg: 'px-6 py-3 text-base',
    xl: 'px-8 py-4 text-lg',
  };

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled || loading}
      className={clsx(
        baseClasses,
        variants[variant],
        sizes[size],
        (disabled || loading) && 'opacity-50 cursor-not-allowed',
        className
      )}
      {...props}
    >
      {loading && (
        <svg className="animate-spin -ml-1 mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
        </svg>
      )}
      {children}
    </button>
  );
};

export const Card = ({ children, className = '', padding = 'md', ...props }) => {
  const paddingClasses = {
    none: '',
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8',
  };

  return (
    <div 
      className={clsx(
        'bg-dark-800 rounded-lg shadow-lg border border-dark-700',
        paddingClasses[padding],
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
};

export const Input = ({ 
  label, 
  error, 
  helper, 
  className = '', 
  required = false,
  ...props 
}) => {
  const id = props.id || props.name;

  return (
    <div className="space-y-1">
      {label && (
        <label htmlFor={id} className="block text-sm font-medium text-gray-300">
          {label}
          {required && <span className="text-red-500 ml-1">*</span>}
        </label>
      )}
      <input
        id={id}
        className={clsx(
          'block w-full rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 bg-dark-700 border-dark-600 text-gray-100',
          error 
            ? 'border-red-500 text-red-400 placeholder-red-400' 
            : 'border-dark-600',
          className
        )}
        {...props}
      />
      {helper && !error && (
        <p className="text-sm text-gray-400">{helper}</p>
      )}
      {error && (
        <p className="text-sm text-red-400">{error}</p>
      )}
    </div>
  );
};

export const Badge = ({ children, variant = 'gray', size = 'md' }) => {
  const variants = {
    gray: 'bg-dark-700 text-gray-300',
    primary: 'bg-primary-900 text-primary-300',
    success: 'bg-green-900 text-green-300',
    warning: 'bg-yellow-900 text-yellow-300',
    error: 'bg-red-900 text-red-300',
  };

  const sizes = {
    sm: 'px-2 py-1 text-xs',
    md: 'px-3 py-1 text-sm',
    lg: 'px-4 py-2 text-base',
  };

  return (
    <span className={clsx(
      'inline-flex items-center rounded-full font-medium',
      variants[variant],
      sizes[size]
    )}>
      {children}
    </span>
  );
};

export const LoadingSpinner = ({ size = 'md' }) => {
  const sizes = {
    sm: 'h-4 w-4',
    md: 'h-8 w-8',
    lg: 'h-12 w-12',
  };

  return (
    <div className="flex justify-center">
      <svg className={clsx('animate-spin text-primary-600', sizes[size])} fill="none" viewBox="0 0 24 24">
        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
      </svg>
    </div>
  );
};
