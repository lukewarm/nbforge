<template>
  <AdminRoute>
    <div class="min-h-screen bg-gray-50">
      <AdminNav />
      <div class="py-6">
        <router-view></router-view>
      </div>
    </div>
  </AdminRoute>
</template>

<script setup>
import AdminRoute from '@/components/AdminRoute.vue'
import AdminNav from '@/components/AdminNav.vue'
</script> 