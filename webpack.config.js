const path = require('path');
const webpack = require('webpack');
const TerserPlugin = require('terser-webpack-plugin');
const {CleanWebpackPlugin} = require('clean-webpack-plugin');
const CopyWebpackPlugin = require('copy-webpack-plugin');
const autoprefixer = require('autoprefixer');


const postcssLoader = (env, options) => {
    return {
        loader: 'postcss-loader',
        options: {
            postcssOptions: {
                plugins: [
                    autoprefixer
                ]
            }
        }
    };
};

const cssFileLoader = (env, options) => {
    return {
        loader: 'file-loader',
        options: {outputPath: 'styles', name: '[name].css'}
    };
};

const commonConfig = (env, options) => {
    let isProduction = options.mode === 'production';
    return {
        name: 'gcampus',
        optimization: {
            minimize: isProduction,
            minimizer: [
                new TerserPlugin()
            ]
        },
        module: {
            rules: [
                {
                    test: /\.css$/,
                    use: [
                        cssFileLoader(env, options),
                        'extract-loader',
                        'css-loader',
                        postcssLoader(env, options)
                    ]
                },
                {
                    test: /\.scss$/,
                    exclude: /node_modules/,
                    use: [
                        cssFileLoader(env, options),
                        'extract-loader',
                        'css-loader',
                        postcssLoader(env, options),
                        {loader: 'sass-loader'}
                    ]
                },
                {
                    test: /\.js$/,
                    loader: 'babel-loader',
                    exclude: /node_modules/,
                    options: {
                        presets: ['@babel/preset-env'],
                        // outputPath: 'js'
                    }
                },
                {
                    test: /\.(png|jpg|gif|svg)$/,
                    loader: 'file-loader',
                    options: {
                        name: '[name].[ext]?[hash]',
                        // publicPath: '/static/assets',
                        outputPath: 'assets',
                        esModule: false,
                    }
                },
                {
                    test: /\.(woff|woff2|eot|ttf|otf)$/,
                    loader: "file-loader",
                    options: {
                        name: '[name].[ext]?[hash]',
                        // publicPath: '/static/fonts',
                        outputPath: 'fonts',
                        esModule: false,
                    }
                }
            ]
        },
        target: 'browserslist',
        plugins: [
            new webpack.ProgressPlugin(),
            new CleanWebpackPlugin()
        ],
        watchOptions: {
            ignored: ['**/*.py', '**/node_modules'],
        },
        performance: {
            hints: 'warning'
        },
        devtool: (isProduction) ? false : 'eval',  // use 'eval-source-map' for higher quality source maps
        watch: !isProduction
    };
}

let gcampuscoreConfig = (env, options) => {
    let common = commonConfig(env, options);
    return Object.assign(common, {
        name: 'gcampuscore',
        entry: {
            main: path.resolve(__dirname, 'gcampus', 'core', 'static_src', 'js', 'index.js'),
            autofocus: path.resolve(__dirname, 'gcampus', 'core', 'static_src', 'js', 'autofocus.js'),
            leafletsearch: path.resolve(__dirname, 'gcampus', 'core', 'static_src', 'js', 'leafletsearch.js'),
            watersuggestion: path.resolve(__dirname, 'gcampus', 'core', 'static_src', 'js', 'watersuggestion.js'),
            dynamicformset: path.resolve(__dirname, 'gcampus', 'core', 'static_src', 'js', 'dynamicformset.js'),
        },
        output: {
            path: path.resolve(__dirname, 'gcampus', 'core', 'static', 'gcampuscore'),
            publicPath: '/static/gcampuscore',
            filename: 'js/[name].js',
            library: {
                name: 'gcampus',
                type: 'var'
            }
        },
        plugins: [
            ...(common.plugins || []),
            new CopyWebpackPlugin({
                patterns: [
                    {
                        from: path.resolve(__dirname, 'gcampus', 'core', 'static_src', 'assets'),
                        to: path.resolve(__dirname, 'gcampus', 'core', 'static', 'gcampuscore', 'assets'),
                    },
                ]
            })
        ],
    });
}

// TODO is this still needed?
module.exports = [gcampuscoreConfig];

module.exports = (env, options) => {
    return [
        gcampuscoreConfig(env, options)
    ];
};
