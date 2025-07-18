const { defineConfig } = require('@vue/cli-service')
module.exports = defineConfig({
  transpileDependencies: true,
  devServer: {
    hot: false,
    liveReload: false,
    client: {
      webSocketURL: {
        hostname: '0.0.0.0',
        pathname: '/ws',
        port: 0  // 0 означает "не использовать WebSocket"
      }
    },
    webSocketServer: false
  }
})