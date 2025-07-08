<template>
    <div id="app">
      <RenderPlanetV2 />
    </div>
  </template>
  


  <script>
  import RenderPlanetV2 from './RenderPlanetV2.vue';
  
  export default {
  components: {
    RenderPlanetV2
  },
  data() {
    return {
      customMarkers: [
        {
          lat: 40.7128,
          lon: -74.0060,
          text: 'New York',
          to: { lat: 34.0522, lon: -118.2437 },
          imageUrl: '/new-york.jpg'
        }
        // More markers...
      ]
    }
  }
}
  </script>
  
  <style>
  /* Global styles */
  </style>