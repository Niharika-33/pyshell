import { createApp } from "vue";
import App from "./App.vue";
import axios from "axios";

// Configure axios defaults
axios.defaults.baseURL = "/";

createApp(App).mount("#app");
