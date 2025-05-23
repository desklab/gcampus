/*
 * Copyright (C) 2021-2022 desklab gUG (haftungsbeschränkt)
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 */

const path = require('path');
const webpack = require('webpack');
const TerserPlugin = require('terser-webpack-plugin');
const {CleanWebpackPlugin} = require('clean-webpack-plugin');
const CopyWebpackPlugin = require('copy-webpack-plugin');
const autoprefixer = require('autoprefixer');
const RemoveEmptyScriptsPlugin = require("webpack-remove-empty-scripts");


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

const cssLoader = (env, options) => {
    return {
        loader: 'css-loader',
        // ES modules had to be disabled because extract-loader is
        // not able to parse the file otherwise.
        options: {esModule: false},
    };
}

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
                        cssLoader(env, options),
                        ...(
                            (options.nopostcssLoader)
                                ? []
                                : [postcssLoader(env, options)]
                        )
                    ]
                },
                {
                    test: /\.scss$/,
                    exclude: /node_modules/,
                    use: [
                        cssFileLoader(env, options),
                        'extract-loader',
                        cssLoader(env, options),
                        ...(
                            (options.nopostcssLoader)
                                ? []
                                : [postcssLoader(env, options)]
                        ),
                        {
                            loader: "sass-loader",
                            options: {
                                api: "legacy",
                            },
                        },
                    ]
                },
                // {
                //     test: /\.js$/,
                //     // loader: 'babel-loader',
                //     exclude: /node_modules/,
                //     options: {
                //         presets: ['@babel/preset-flow'],
                //         // outputPath: 'js'
                //     }
                // },
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
            ...(
                (isProduction)
                    ? []
                    : [new webpack.ProgressPlugin()]
            ),
            new CleanWebpackPlugin()
        ],
        watchOptions: {
            ignored: ['**/*.py', '/node_modules/'],
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
            watersuggestion: path.resolve(__dirname, 'gcampus', 'core', 'static_src', 'js', 'watersuggestion.js'),
            dynamicformset: path.resolve(__dirname, 'gcampus', 'core', 'static_src', 'js', 'dynamicformset.js'),
            filter: path.resolve(__dirname, 'gcampus', 'core', 'static_src', 'js', 'filter.js'),
        },
        output: {
            path: path.resolve(__dirname, 'gcampus', 'core', 'static', 'gcampuscore'),
            publicPath: '/static/gcampuscore',
            filename: 'js/[name].js',
            library: {
                name: ['gcampuscore', '[name]'],
                type: 'var'
            }
        },
        // Enable lines below if assets are needed
        plugins: [
            ...(common.plugins || []),
            new CopyWebpackPlugin({
                patterns: [
                    {
                        from: 'fonts/*.{ttf,woff2}',
                        to: path.resolve(__dirname, 'gcampus', 'core', 'static', 'gcampuscore'),
                        context: path.resolve(__dirname, 'gcampus', 'core', 'static_src'),
                    },
                    {
                        from: 'assets/*.{png,jpg,svg}',
                        to: path.resolve(__dirname, 'gcampus', 'core', 'static', 'gcampuscore'),
                        context: path.resolve(__dirname, 'gcampus', 'core', 'static_src'),
                    },
                ]
            })
        ],
    });
}

let gcampusmapConfig = (env, options) => {
    let common = commonConfig(env, options);
    return Object.assign(common, {
        name: 'gcampusmap',
        entry: {
            'mapbox-gl': path.resolve(__dirname, 'gcampus', 'map', 'static_src', 'js', 'mapbox-gl.js'),
        },
        output: {
            path: path.resolve(__dirname, 'gcampus', 'map', 'static', 'gcampusmap'),
            publicPath: '/static/gcampusmap',
            filename: 'js/[name].js',
            library: {
                name: ['gcampusmap', '[name]'],
                type: 'var'
            }
        },
    });
}

let gcampusauthConfig = (env, options) => {
    let common = commonConfig(env, options);
    return Object.assign(common, {
        name: 'gcampusauth',
        entry: {},
        output: {
            path: path.resolve(__dirname, 'gcampus', 'auth', 'static', 'gcampusauth'),
            publicPath: '/static/gcampusauth',
            filename: 'js/[name].js',
            library: {
                name: ['gcampusauth', '[name]'],
                type: 'var'
            }
        },
        plugins: [
            ...(common.plugins || []),
            new CopyWebpackPlugin({
                patterns: [
                    {
                        from: 'fonts/*.{ttf,woff2}',
                        to: path.resolve(__dirname, 'gcampus', 'auth', 'static', 'gcampusauth'),
                        context: path.resolve(__dirname, 'gcampus', 'auth', 'static_src'),
                    },
                ]
            })
        ],
    });
}

let gcampusdocumentsConfig = (env, options) => {
    let common = commonConfig(env, options);
    return Object.assign(common, {
        name: 'gcampusdocuments',
        entry: {
            'gcampus': path.resolve(__dirname, 'gcampus', 'documents', 'static_src', 'styles', 'gcampus.scss'),
        },
        output: {
            path: path.resolve(__dirname, 'gcampus', 'documents', 'static', 'gcampusdocuments'),
            publicPath: '/static/gcampusdocuments',
            filename: 'js/[name].js',
            library: {
                name: ['gcampusdocuments', '[name]'],
                type: 'var'
            }
        },
        plugins: [
            ...(common.plugins || []),
            new RemoveEmptyScriptsPlugin(),
            new CopyWebpackPlugin({
                patterns: [
                    {
                        from: 'assets/*.{png,jpg,svg}',
                        to: path.resolve(__dirname, 'gcampus', 'documents', 'static', 'gcampusdocuments'),
                        context: path.resolve(__dirname, 'gcampus', 'documents', 'static_src'),
                    },
                ]
            }),
        ],
    });
}

let gcampusmailConfig = (env, options) => {
    options.nopostcssLoader = true
    let common = commonConfig(env, options);
    return Object.assign(common, {
        name: 'gcampusmail',
        entry: {
            'mail': path.resolve(__dirname, 'gcampus', 'mail', 'static_src', 'styles', 'mail.scss'),
        },
        output: {
            path: path.resolve(__dirname, 'gcampus', 'mail', 'static', 'gcampusmail'),
            publicPath: '/static/gcampusmail',
            filename: 'js/[name].js',
            library: {
                name: ['gcampusmail', '[name]'],
                type: 'var'
            }
        },
        plugins: [
            ...(common.plugins || []),
            new RemoveEmptyScriptsPlugin(),
        ],
    });
}

let gcampustoolsConfig = (env, options) => {
    let common = commonConfig(env, options);
    return Object.assign(common, {
        name: 'gcampustools',
        entry: {
            calibration: path.resolve(__dirname, 'gcampus', 'tools', 'static_src', 'js', 'calibration.js'),
        },
        output: {
            path: path.resolve(__dirname, 'gcampus', 'tools', 'static', 'gcampustools'),
            publicPath: '/static/gcampustools',
            filename: 'js/[name].js',
            library: {
                name: ['gcampustools', '[name]'],
                type: 'var'
            }
        },
    });
}



module.exports = (env, options) => {
    return [
        gcampuscoreConfig(env, options),
        gcampusmapConfig(env, options),
        gcampusauthConfig(env, options),
        gcampusdocumentsConfig(env, options),
        gcampusmailConfig(env, options),
        gcampustoolsConfig(env, options),
    ];
};
