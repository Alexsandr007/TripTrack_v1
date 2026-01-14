<template>
  <div id="app">
    <!-- Preloader Component -->
    <Preloader
      :progress="progress"
      :is-curtain-closed="isCurtainClosed"
      :show-curtain="showCurtain"
    />
    
    <!-- Header Component -->
    <Header />
    
    <!-- Router View с блокировкой -->
    <div class="router-container">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" :key="$route.path" />
        </transition>
      </router-view>
    </div>         
  </div>
</template>

<script>
import Preloader from '@/components/Preloader.vue'
import Header from '@/components/home/include/HeaderComponent.vue'

export default {
  name: 'App',
  components: {
    Header,
    Preloader
  },
  data() {
    return {
      progress: 0,
      isCurtainClosed: false,
      isLoading: false,
      showCurtain: false,
      progressInterval: null
    }
  },
  watch: {
    $route() {
      this.startPageTransition()
    }
  },
  mounted() {
    this.startPageTransition()
  },
  beforeUnmount() {
    if (this.progressInterval) {
      clearInterval(this.progressInterval)
    }
  },
  methods: {
    startPageTransition() {
      this.progress = 0
      this.isCurtainClosed = false
      this.isLoading = true
      this.showCurtain = true

      setTimeout(() => {
        this.isCurtainClosed = true
        
        setTimeout(() => {
          this.startProgress()
        }, 100)
      }, 50)
    },
    startProgress() {
      if (this.progressInterval) {
        clearInterval(this.progressInterval)
      }

      this.progressInterval = setInterval(() => {
        this.progress += 10
        
        if (this.progress >= 100) {
          clearInterval(this.progressInterval)
          this.progress = 100
          this.completeTransition()
        }
      }, 120)
    },
    completeTransition() {
      this.isLoading = false
      
      setTimeout(() => {
        this.isCurtainClosed = false
        
        setTimeout(() => {
          this.showCurtain = false
          this.progress = 0
        }, 600)
      }, 300)
    }
  }
}
</script>

<style>
#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.main-content {
  flex: 1;
  padding-bottom: 60px; /* Высота футера */
}

.router-container {
  position: relative;
  z-index: 1;
}

/* Fade transition для контента */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.4s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>