<template>
  <div>
    <h2>Register</h2>
    <input v-model="username" placeholder="Email" />
    <input v-model="password" type="password" placeholder="Password" />
    <input v-model="fullname" placeholder="Full Name" />
    <input v-model="qualification" placeholder="Qualification" />
    <input v-model="email" placeholder="email" />
    <button @click="register">Register</button>
    <p>Already have an account? <router-link to="/login">Login</router-link></p>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  data() {
    return {
      username: '',
      password: '',
      fullname: '',
      qualification: '',
      email:'',
      last_login :'',
      preferred_reminder_time:''
    }
  },
  methods: {
    async register() {
      try {
        await axios.post('http://localhost:5000/register', {
          username: this.username,                     
          password: this.password,
          fullname: this.fullname,
          qualification: this.qualification,
          email: this.email,
          last_login :this.last_login,
          preferred_reminder_time:this.preferred_reminder_time
        })
        alert('Registered successfully!')
        this.$router.push('/login')
      } catch (err) {
        alert(err.response?.data?.msg || 'Registration failed')
      }
    }
  }
}
</script>
