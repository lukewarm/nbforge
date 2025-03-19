<template>
  <div 
    class="relative bg-gray-200 flex items-center justify-center overflow-hidden" 
    :class="[
      sizeClasses, 
      rounded ? 'rounded-full' : 'rounded-md',
      className
    ]"
  >
    <img 
      v-if="!avatarLoadError" 
      :src="avatarUrl" 
      :alt="alt || `${user?.username || 'User'}'s avatar`"
      class="h-full w-full object-cover"
      @error="onAvatarError"
    />
    <span 
      v-if="avatarLoadError" 
      class="font-semibold text-gray-700"
      :class="[initialsSize]"
    >
      {{ initials }}
    </span>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { getUserAvatar, GRAVATAR_DEFAULTS } from '@/utils/avatar';

const props = defineProps({
  user: {
    type: Object,
    default: null
  },
  size: {
    type: String,
    default: 'md',
    validator: (value) => ['xs', 'sm', 'md', 'lg', 'xl', '2xl'].includes(value)
  },
  rounded: {
    type: Boolean,
    default: true
  },
  defaultStyle: {
    type: String,
    default: GRAVATAR_DEFAULTS.IDENTICON,
    validator: (value) => Object.values(GRAVATAR_DEFAULTS).includes(value)
  },
  className: {
    type: String,
    default: ''
  },
  alt: {
    type: String,
    default: ''
  }
});

const avatarLoadError = ref(false);

const sizeMap = {
  'xs': { container: 'h-8 w-8', text: 'text-xs' },
  'sm': { container: 'h-10 w-10', text: 'text-sm' },
  'md': { container: 'h-12 w-12', text: 'text-base' },
  'lg': { container: 'h-16 w-16', text: 'text-xl' },
  'xl': { container: 'h-20 w-20', text: 'text-2xl' },
  '2xl': { container: 'h-24 w-24', text: 'text-3xl' }
};

const pixelSizeMap = {
  'xs': 32,
  'sm': 40,
  'md': 48,
  'lg': 64,
  'xl': 80,
  '2xl': 96
};

const sizeClasses = computed(() => sizeMap[props.size]?.container || sizeMap.md.container);
const initialsSize = computed(() => sizeMap[props.size]?.text || sizeMap.md.text);
const pixelSize = computed(() => pixelSizeMap[props.size] || 48);

const avatarInfo = computed(() => {
  return getUserAvatar(props.user, {
    size: pixelSize.value,
    defaultStyle: props.defaultStyle
  });
});

const avatarUrl = computed(() => avatarInfo.value.url);
const initials = computed(() => avatarInfo.value.initials);

function onAvatarError() {
  avatarLoadError.value = true;
}

// Reset the error state if the user prop changes
onMounted(() => {
  avatarLoadError.value = false;
});
</script> 