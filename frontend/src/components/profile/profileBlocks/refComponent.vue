<template>
  <div class="ref-component profile-block">
    <h3>Реферальная система</h3>
    
    <div class="referral-stats">
      <div class="stat">
        <span class="stat-number">45</span>
        <span class="stat-label">Всего рефералов</span>
      </div>
      <div class="stat">
        <span class="stat-number">32</span>
        <span class="stat-label">Активных</span>
      </div>
    </div>
    
    <div class="referral-link">
      <label>Ваша реферальная ссылка:</label>
      <div class="link-container">
        <input value="https://t.me/yourbot?start=ref123456" readonly class="link-input" />
        <button class="copy-btn">📋</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'RefComponent'
}
</script>

<style scoped>
.ref-component h3 {
  color: white;
  margin-bottom: 20px;
}

.referral-stats {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
  margin-bottom: 20px;
}

.stat {
  text-align: center;
  padding: 15px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
}

.stat-number {
  display: block;
  color: #25438B;
  font-size: 1.5rem;
  font-weight: bold;
}

.stat-label {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.8rem;
}

.referral-link label {
  display: block;
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 10px;
  font-size: 0.9rem;
}

.link-container {
  display: flex;
  gap: 10px;
}

.link-input {
  flex: 1;
  padding: 10px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 6px;
  color: white;
  font-size: 0.9rem;
}

.copy-btn {
  padding: 10px 15px;
  background: #25438B;
  border: none;
  border-radius: 6px;
  color: white;
  cursor: pointer;
}

.profile-block {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border-radius: 15px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 25px;
  margin-bottom: 20px;
}
</style>