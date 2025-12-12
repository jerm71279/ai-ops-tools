module.exports = {
  entry: './src/index.js',
  module: {
    rules: [
      {
        test: /\.(js|jsx)$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader'
        }
      }
    ]
  },
  resolve: {
    modules: ['node_modules', './node_modules']
  },
  output: {
    path: __dirname + '/dist',
    filename: 'bundle.js'
  }
};