const path = require('path');
const webpack = require('webpack');
const TerserPlugin = require('terser-webpack-plugin');
const { CleanWebpackPlugin } = require('clean-webpack-plugin');
const CopyWebpackPlugin = require('copy-webpack-plugin');


module.exports = {
  name: 'gcampus',
  entry: {
    main: './src/main.js',
  },
  output: {
    path: path.resolve(__dirname, '..', 'gcampus', 'core', 'static', 'gcampuscore'),
    publicPath: '/static/',
    filename: '[name].bundle.js'
  },
  optimization: {
    splitChunks: {
      chunks: 'all',
      name: 'vendor',
      minChunks: 2
    },
    runtimeChunk: {
      name: 'runtime'
    },
    minimize: process.env.NODE_ENV === 'production',
    minimizer: [
      new TerserPlugin()
    ]
  },
  module: {
    rules: [
      {
        test: /\.css$/,
        use: [
          {
            loader: 'file-loader',
            options: {outputPath: 'css/', name: '[name].min.css'}
          },
          'extract-loader',
          'css-loader',
          {
            loader: 'postcss-loader',
            options: {
              postcssOptions: {
                plugins: [
                  require('autoprefixer')
                ]
              }
            }
          },
        ],
      },
      {
        test: /\.scss$/,
        exclude: /node_modules/,
        use: [
          {
            loader: 'file-loader',
            options: {outputPath: 'css/', name: '[name].min.css'}
          },
          'extract-loader',
          'css-loader',
          {
            loader: 'postcss-loader',
            options: {
              postcssOptions: {
                plugins: [
                  require('autoprefixer')
                ]
              }
            }
          },
          {
            loader: 'sass-loader'
          },
        ]
      },
      {
        test: /\.js$/,
        loader: 'babel-loader',
        exclude: /node_modules/,
        options: {
          presets: ['@babel/preset-env']
        }
      },
      {
        test: /\.(png|jpg|gif|svg)$/,
        loader: 'file-loader',
        options: {
          name: '[name].[ext]?[hash]',
          publicPath: '/static/assets',
          outputPath: 'assets',
          esModule: false,
        }
      },
      {
        test: /\.(woff|woff2|eot|ttf|otf)$/,
        loader: "file-loader",
        options: {
          name: '[name].[ext]?[hash]',
          publicPath: '/static/fonts',
          outputPath: 'fonts',
          esModule: false,
        }
      }
    ]
  },
  plugins: [
    new CleanWebpackPlugin(),
    // new CopyWebpackPlugin({
    //   patterns: [
    //     { 
    //       from: path.resolve(__dirname, ...),
    //       to: path.resolve(__dirname, ...)
    //     }
    //   ]
    // })
  ],
  watchOptions: {
    // ignored: /node_modules/
  },
  performance: {
    hints: false
  },
  devtool: 'eval-source-map',
  mode: process.env.NODE_ENV
}