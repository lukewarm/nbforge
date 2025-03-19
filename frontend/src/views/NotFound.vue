<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full text-center">
      <h1 class="text-9xl font-bold text-indigo-600">404</h1>
      <h2 class="mt-6 text-3xl font-extrabold text-gray-900">
        Page Not Found
      </h2>
      <p class="mt-2 text-gray-600">
        The page you're looking for doesn't exist or has been moved.
      </p>
      <div class="mt-8">
        <router-link 
          to="/" 
          class="inline-flex items-center px-4 py-2 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
        >
          Go back home
        </router-link>
      </div>
    </div>
  </div>
</template> 