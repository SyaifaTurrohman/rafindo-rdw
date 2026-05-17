<template>
  <div class="min-h-screen bg-gray-100 flex flex-col items-center justify-center p-4 font-sans text-gray-800">
    
    <header class="mb-6 text-center">
      <h1 class="text-3xl font-extrabold text-blue-700 tracking-wide">RAFINDO DIGITAL WORKSTATION (RDW)</h1>
    </header>

    <div v-if="!isLoggedIn" class="w-full max-w-md bg-white rounded-2xl shadow-xl p-8 border border-gray-200">
      <h2 class="text-xl font-bold text-center mb-6 text-gray-700">Login</h2>
      
      <div v-if="errorMessage" class="mb-4 p-3 bg-red-100 text-red-750 text-sm rounded-lg font-medium">
        ⚠️ {{ errorMessage }}
      </div>

      <form @submit.prevent="handleLogin" class="space-y-4">
        <div>
          <label class="block text-xs font-semibold uppercase tracking-wider text-gray-500 mb-1">Email</label>
          <input 
            v-model="loginForm.email" 
            type="email" 
            class="w-full px-4 py-3 bg-gray-50 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:outline-none transition-all"
            required
          />
        </div>
        <div>
          <label class="block text-xs font-semibold uppercase tracking-wider text-gray-500 mb-1">Password</label>
          <input 
            v-model="loginForm.password" 
            type="password" 
            class="w-full px-4 py-3 bg-gray-50 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:outline-none transition-all"
            required
          />
        </div>
        <button 
          type="submit" 
          class="w-full py-3 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-xl shadow-lg transition-all transform active:scale-95 mt-2"
        >
          Masuk ke Workstation
        </button>
      </form>
    </div>

    <div v-else class="w-full max-w-2xl bg-white rounded-3xl shadow-2xl p-6 md:p-8 border border-gray-150 grid grid-cols-1 md:grid-cols-12 gap-6">
      
      <div class="md:col-span-5 flex flex-col justify-between border-b md:border-b-0 md:border-r border-gray-200 pb-6 md:pb-0 md:pr-6">
        <div>
          <div class="inline-flex items-center gap-1.5 px-3 py-1 bg-green-100 text-green-700 rounded-full text-xs font-bold mb-4">
            <span class="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span> Terhubung
          </div>
          <h2 class="text-2xl font-black text-gray-800 mb-1">{{ user.role }}</h2>
          <p class="text-sm text-gray-500 font-mono mb-6">{{ user.email }}</p>
          
          <div class="bg-blue-50 rounded-2xl p-4 text-center border border-blue-150">
            <span class="block text-xs font-bold text-blue-600 uppercase tracking-widest mb-1">Angka Dasar</span>
            <span class="text-5xl font-black text-blue-700 font-mono">{{ user.angka_dasar }}</span>
          </div>
        </div>

        <button 
          @click="handleLogout" 
          class="mt-6 w-full py-2.5 bg-gray-150 hover:bg-gray-200 text-gray-600 font-bold rounded-xl text-sm transition-all text-center"
        >
          Logout
        </button>
      </div>

      <div class="md:col-span-7 flex flex-col justify-between space-y-4">
        
        <div v-if="calcMessage" class="p-3 text-sm rounded-xl font-medium" :class="calcStatus === 'success' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'">
          {{ calcMessage }}
        </div>

        <div>
          <label class="block text-xs font-bold uppercase tracking-wider text-gray-500 mb-1">Input Angka (0 - 9)</label>
          <input 
            v-model="calcInput" 
            type="text" 
            maxlength="1"
            placeholder="Pilih atau ketik angka"
            @input="validateKeyboardInput"
            class="w-full text-center text-2xl font-mono font-bold px-4 py-3 bg-gray-50 border-2 border-gray-200 rounded-xl focus:border-blue-500 focus:outline-none transition-all"
          />
        </div>

        <div class="grid grid-cols-3 gap-2">
          <button 
            v-for="num in ['1','2','3','4','5','6','7','8','9','0']" 
            :key="num"
            @click="pressNumber(num)"
            class="py-3 bg-gray-100 hover:bg-gray-200 active:bg-gray-300 text-lg font-bold rounded-xl transition-all border border-gray-200 shadow-sm"
            :class="num === '0' ? 'col-span-2' : ''"
          >
            {{ num }}
          </button>
          <button 
            @click="clearInput"
            class="py-3 bg-red-50 hover:bg-red-100 text-red-600 font-bold rounded-xl border border-red-200 transition-all"
          >
            C
          </button>
        </div>

        <div class="grid grid-cols-2 gap-3 pt-2">
          <button 
            @click="sendCalculation('tambah')"
            class="py-4 bg-blue-600 hover:bg-blue-700 text-white font-extrabold text-lg rounded-2xl shadow-md transition-all transform active:scale-95 flex items-center justify-center gap-2"
          >
            <span>➕</span> TAMBAH
          </button>
          <button 
            @click="sendCalculation('kurang')"
            class="py-4 bg-amber-500 hover:bg-amber-600 text-white font-extrabold text-lg rounded-2xl shadow-md transition-all transform active:scale-95 flex items-center justify-center gap-2"
          >
            <span>➖</span> KURANG
          </button>
        </div>

        <div class="mt-4 p-4 bg-gray-900 rounded-2xl text-center text-white font-mono border-2 border-gray-800 shadow-inner">
          <span class="block text-xs font-bold text-gray-400 uppercase tracking-widest mb-1">Hasil</span>
          <span class="text-4xl font-black text-green-400">{{ displayResult }}</span>
        </div>

      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, reactive } from 'vue';

// Konfigurasi URL API Python Backend
const API_BASE_URL = 'http://127.0.0.1:5000/api';

// State Autentikasi
const isLoggedIn = ref(false);
const errorMessage = ref('');
const loginForm = reactive({ email: '', password: '' });
const user = reactive({ email: '', role: '', angka_dasar: 0 });

// State Kalkulator
const calcInput = ref('');
const displayResult = ref('---');
const calcMessage = ref('');
const calcStatus = ref('');

// Fungsi Login terintegrasi ke Python API
const handleLogin = async () => {
  errorMessage.value = '';
  try {
    const response = await fetch(`${API_BASE_URL}/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(loginForm)
    });
    const data = await response.json();

    if (response.ok) {
      isLoggedIn.value = true;
      user.email = data.user.email;
      user.role = data.user.role;
      user.angka_dasar = data.user.angka_dasar;
    } else {
      errorMessage.value = data.message || 'Login gagal!';
    }
  } catch (error) {
    errorMessage.value = 'Tidak dapat terhubung ke server backend Python!';
  }
};

// Fungsi Logout
const handleLogout = () => {
  isLoggedIn.value = false;
  loginForm.email = '';
  loginForm.password = '';
  clearInput();
  displayResult.value = '---';
};

// Validasi input keyboard biar beneran cuma 0-9
const validateKeyboardInput = () => {
  calcInput.value = calcInput.value.replace(/[^0-9]/g, '');
  if (calcInput.value.length > 1) {
    calcInput.value = calcInput.value.charAt(0);
  }
};

// Aksi ketika tombol On-Screen Numberpad ditekan
const pressNumber = (num) => {
  calcInput.value = num; 
  calcMessage.value = '';
};

// Bersihkan input
const clearInput = () => {
  calcInput.value = '';
  calcMessage.value = '';
};

// Mengirim instruksi kalkulasi ke Python Backend secara Asinkronus (Tanpa Reload)
const sendCalculation = async (operasi) => {
  if (calcInput.value === '') {
    calcStatus.value = 'error';
    calcMessage.value = 'Pilih angka terlebih dahulu!';
    return;
  }

  try {
    const response = await fetch(`${API_BASE_URL}/calculate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: user.email,
        angka: calcInput.value,
        operasi: operasi
      })
    });
    const data = await response.json();

    if (response.ok) {
      calcStatus.value = 'success';
      calcMessage.value = `Berhasil melakukan ${operasi}!`;
      displayResult.value = data.hasil; // Update state hasil kalkulasi secara real-time
    } else {
      calcStatus.value = 'error';
      calcMessage.value = data.message;
    }
  } catch (error) {
    calcStatus.value = 'error';
    calcMessage.value = 'Gagal memproses kalkulasi ke server.';
  }
};
</script>