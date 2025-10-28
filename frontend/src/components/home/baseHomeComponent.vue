<template>
  <div>
      <RenderPlanetV2 />
      <RenderInformationBlockMain />
      <Footer />
  </div>

  </template>
  


  <script>
  import RenderPlanetV2 from './blocks/RenderPlanet.vue';
  import RenderInformationBlockMain from './blocks/RenderInformationBlockMain.vue';
  import Footer from './include/FooterComponent.vue';
  
  export default {
    components: {
      RenderPlanetV2,
      RenderInformationBlockMain,
      Footer,
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
      ],
      isLoading: true,
      loadProgress: 0
    }
  },
  mounted() {
    // Симуляция загрузки
    setTimeout(() => {
      this.isLoading = false
    }, 2000)
  },
}
  </script>
  
  <style>
  body{
    padding: 0px;
    margin: 0px;
  }
  </style>
