<template>
    <div>
      <h1>Create Item</h1>
      <form @submit.prevent="createItem">
        <input v-model="name" placeholder="Name" required />
        <textarea v-model="description" placeholder="Description" required></textarea>
        <button type="submit">Create</button>
      </form>
    </div>
  </template>
  
  <script>
  import axios from 'axios';
  
  export default {
    data() {
      return {
        name: '',
        description: ''
      };
    },
    methods: {
      createItem() {
        axios.post('http://localhost:8000/api/items/', {
          name: this.name,
          description: this.description
        }).then(response => {
          console.log('Item created:', response.data);
          this.name = '';
          this.description = '';
        });
      }
    }
  };
  </script>