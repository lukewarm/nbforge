/**
 * Utility functions for handling user avatars
 */
import md5 from 'md5';

/**
 * Available Gravatar default styles
 */
export const GRAVATAR_DEFAULTS = {
  MP: 'mp',          // Mystery Person (generic silhouette)
  IDENTICON: 'identicon', // Geometric pattern based on email hash
  MONSTERID: 'monsterid', // Monster cartoon face
  WAVATAR: 'wavatar',   // Cartoon face
  RETRO: 'retro',     // 8-bit style pixelated face
  ROBOHASH: 'robohash'  // Robot avatar
};

/**
 * Get Gravatar URL for an email address
 * @param {string} email - User's email address
 * @param {Object} options - Gravatar options
 * @param {number} options.size - Size in pixels (1-2048)
 * @param {string} options.defaultImage - Default image type from GRAVATAR_DEFAULTS
 * @param {boolean} options.forceDefault - Always use default image even if Gravatar exists
 * @returns {string} Gravatar URL
 */
export function getGravatarUrl(email, options = {}) {
  if (!email) {
    return getDefaultAvatarUrl(options);
  }
  
  const hash = md5(email.trim().toLowerCase());
  const size = options.size || 80;
  const defaultImage = options.defaultImage || GRAVATAR_DEFAULTS.IDENTICON;
  const forceDefault = options.forceDefault ? 'f=y' : '';
  
  return `https://www.gravatar.com/avatar/${hash}?s=${size}&d=${defaultImage}${forceDefault ? '&' + forceDefault : ''}`;
}

/**
 * Get a local default avatar URL
 * @param {Object} options - Options
 * @param {number} options.size - Size in pixels
 * @returns {string} Local avatar URL
 */
export function getDefaultAvatarUrl(options = {}) {
  // Use our SVG file
  return '/images/default-avatar.svg';
}

/**
 * Generate user initials from name
 * @param {string} name - User's full name
 * @returns {string} User's initials (max 2 characters)
 */
export function getUserInitials(name) {
  if (!name) return '?';
  
  const parts = name.trim().split(/\s+/);
  if (parts.length === 1) {
    return parts[0].charAt(0).toUpperCase();
  }
  
  return (parts[0].charAt(0) + parts[parts.length - 1].charAt(0)).toUpperCase();
}

/**
 * Get appropriate avatar for a user
 * 
 * Handles multiple fallback options:
 * 1. User-provided avatar
 * 2. Gravatar based on email
 * 3. Local default avatar with user initials
 * 
 * @param {Object} user - User object
 * @param {string} user.avatar - Custom avatar URL (optional)
 * @param {string} user.email - User's email (optional)
 * @param {string} user.full_name - User's full name (optional)
 * @param {Object} options - Avatar options
 * @returns {Object} Avatar info including URL and fallback data
 */
export function getUserAvatar(user, options = {}) {
  const size = options.size || 80;
  const defaultStyle = options.defaultStyle || GRAVATAR_DEFAULTS.IDENTICON;
  
  // Case 1: User has a custom avatar
  if (user?.avatar) {
    return {
      type: 'custom',
      url: user.avatar,
      initials: getUserInitials(user?.full_name || user?.username || '')
    };
  }
  
  // Case 2: User has an email, try Gravatar
  if (user?.email) {
    return {
      type: 'gravatar',
      url: getGravatarUrl(user.email, { size, defaultImage: defaultStyle }),
      initials: getUserInitials(user?.full_name || user?.username || '')
    };
  }
  
  // Case 3: Fallback to default
  return {
    type: 'default',
    url: getDefaultAvatarUrl({ size }),
    initials: getUserInitials(user?.full_name || user?.username || '')
  };
}

export default {
  getGravatarUrl,
  getDefaultAvatarUrl,
  getUserInitials,
  getUserAvatar,
  GRAVATAR_DEFAULTS
}; 