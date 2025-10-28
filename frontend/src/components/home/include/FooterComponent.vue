<template>
  <footer class="footer">
    <div class="footer-content">
      <!-- Логотип слева -->
      <div class="logo">
        <img src="../../../assets/img/home/logo_planet.png" alt="Logo">
      </div>
      
      <!-- Ссылки и копирайт справа -->
      <div class="footer-links">
        <p class="copyright">&copy; 2023 Your Company. All rights reserved.</p>
        <div class="links">
          <button class="btn link-btn" @click="handleAbout">О нас</button>
          <button class="btn link-btn" @click="handleContacts">Контакты</button>
          <button class="btn link-btn" @click="handlePrivacy">Политика конфиденциальности</button>
        </div>
      </div>
    </div>
  </footer>
</template>

<script>
import { defineComponent } from 'vue';

export default defineComponent({
  name: 'FooterComponent',
  emits: ['about', 'contacts', 'privacy'],
  setup(props, { emit }) {
    const handleAbout = () => {
      emit('about');
    };
    
    const handleContacts = () => {
      emit('contacts');
    };
    
    const handlePrivacy = () => {
      emit('privacy');
    };
    
    return {
      handleAbout,
      handleContacts,
      handlePrivacy
    };
  }
});
</script>

<style scoped>
.footer {
  position: relative;
  bottom: 0;
  left: 0;
  width: 100%;
  background: linear-gradient(to right, #020C2B 0%, #25438B 50%, #030516 100%); /* Сплошной градиентный фон */
  z-index: 10;
  border-top: 1px solid rgba(37, 67, 139, 0.2);
}

.footer-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;
  padding: 15px 20px;
}

.logo {
  display: flex;
  align-items: center;
}

.logo img {
  width: 40px;
  height: 40px;
  transition: transform 0.3s ease;
}

.logo img:hover {
  transform: rotate(-10deg) scale(1.1); /* Легкий поворот в другую сторону для разнообразия */
}

.footer-links {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 5px;
}

.copyright {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.8);
  margin: 0;
}

.links {
  display: flex;
  gap: 15px;
}

.btn {
  padding: 8px 16px; /* Немного меньше, чем в header, для компактности */
  border: 2px solid #ffffff80;
  background: transparent;
  color: #ffffff80;
  font-size: 0.9rem;
  font-weight: 500;
  border-radius: 25px;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(to right, #020C2B 0%, #25438B 50%, #030516 100%);
  transition: left 0.3s ease;
  z-index: -1;
}

.btn:hover {
  color: white;
  border-color: #25438B;
  box-shadow: 0 4px 15px rgba(37, 67, 139, 0.3);
}

.btn:hover::before {
  left: 0;
}

.link-btn:hover {
  background: linear-gradient(to right, #020C2B 0%, #25438B 50%, #030516 100%);
}

/* Адаптивность */
@media (max-width: 768px) {
  .footer-content {
    padding: 10px 15px;
    flex-direction: column; /* Стек элементов вертикально на мобильных */
    gap: 10px;
  }
  
  .footer-links {
    align-items: center; /* Центрирование на мобильных */
  }
  
  .links {
    flex-wrap: wrap; /* Перенос ссылок, если не помещаются */
    justify-content: center;
  }
  
  .btn {
    padding: 6px 12px;
    font-size: 0.8rem;
  }
  
  .logo img {
    width: 35px;
    height: 35px;
  }
  
  .copyright {
    font-size: 0.8rem;
  }
}
</style>