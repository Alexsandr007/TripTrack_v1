import { createRouter, createWebHistory } from 'vue-router';
import baseHomeComponent from '../components/home/baseHomeComponent.vue'
import RegisterComponent from '../components/home/auth/RegisterComponent.vue'; // Убедитесь, что файл называется RegisterComponent.vue
import Login from '../components/home/auth/LoginComponent.vue'
import Recovery from '../components/home/auth/RecoveryComponent.vue'
import Profile from '../components/profile/profileComponent.vue'

const routes = [
  { path: '/', name: 'Home', component: baseHomeComponent },
  { path: '/login', name: 'Login', component: Login },
  { path: '/register', name: 'Register', component: RegisterComponent },
  { path: '/recovery', name: 'Recovery', component: Recovery },
  { path: '/profile', name: 'Profile', component: Profile }
  
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;