import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    port: 3000,
    proxy: {
      "/execute": "http://localhost:5000",
      "/history": "http://localhost:5000",
      "/clear-history": "http://localhost:5000",
    },
  },
});
