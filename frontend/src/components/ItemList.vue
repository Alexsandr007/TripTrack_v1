<template>
    <div>
      <h1>Items</h1>
      <ul>
        <li v-for="item in items" :key="item.id">{{ item.name }}: {{ item.description }}</li>
      </ul>
    </div>
  </template>
  
  <script>
  import axios from 'axios';
  
  export default {
    data() {
      return {
        items: []
      };
    },
    created() {
      axios.get('http://localhost:8000/api/items/')
        .then(response => {
          this.items = response.data;
        });
    }
  };
  </script>