const path = require('path');

module.exports = {
  // Other configurations...
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'components')
    },
    extensions: ['.js', '.jsx', '.ts', '.tsx']
  }
};
