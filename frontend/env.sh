#!/bin/bash

# Define the directory where the app is served
APP_DIR=/usr/share/nginx/html

# Create the env-config.js file that will be loaded by the app
echo "window.env = {" > $APP_DIR/env-config.js

# Add API URL from environment variable or use default
echo "  API_URL: \"${VITE_API_URL:-/api/v1}\"," >> $APP_DIR/env-config.js

# Add other environment variables as needed
echo "  NODE_ENV: \"${NODE_ENV:-production}\"," >> $APP_DIR/env-config.js
echo "  BASE_URL: \"${BASE_URL:-/}\"," >> $APP_DIR/env-config.js

# Add any other VITE_ prefixed variables
for envvar in $(env | grep '^VITE_' | sed 's/=.*//'); do
  # Skip VITE_API_URL as we've already added it
  if [ "$envvar" != "VITE_API_URL" ]; then
    value=$(eval echo \$$envvar)
    # Convert VITE_VARIABLE_NAME to variableName (camelCase)
    name=$(echo $envvar | sed 's/^VITE_//' | sed 's/_\([a-z]\)/\U\1/g' | sed 's/^./\L&/')
    echo "  $name: \"$value\"," >> $APP_DIR/env-config.js
  fi
done

# Close the object
echo "};" >> $APP_DIR/env-config.js

# Add script tag to index.html to load env-config.js before the application
sed -i '/<head>/a\    <script src="/env-config.js"></script>' $APP_DIR/index.html

echo "Environment configuration generated at $APP_DIR/env-config.js" 