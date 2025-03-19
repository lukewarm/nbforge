// This script handles direct URL access to notebook paths
(function() {
  // When loaded directly, check if we need to fix encoding
  if (window.location.pathname.includes('/notebooks/')) {
    var path = window.location.pathname;
    // Fix common encoding issues
    if (path.includes('%252F')) {
      // Double-encoded slashes, decode once
      path = path.replace(/%252F/g, '%2F');
      window.history.replaceState(null, '', path + window.location.search);
    }
  }
})(); 