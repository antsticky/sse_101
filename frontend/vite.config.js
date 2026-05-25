export default {
  server: {
    proxy: {
      "/start": "http://localhost:8000",
      "/events": {
        target: "http://localhost:8000",
        changeOrigin: true,
        ws: false,
      },
    },
  },
};
