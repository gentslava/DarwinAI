const path = require('path');
const webpack = require('webpack');
const HtmlWebpackPlugin = require('html-webpack-plugin');

module.exports = ({ mode } = { mode: 'production' }) => {
    console.log(`mode is: ${mode}`);

    return {
        mode,
        entry: './src/index.js',
        devServer: {
            hot: true,
            open: true,
        },
        output: {
            publicPath: '/',
            path: path.resolve(__dirname, 'build'),
            filename: 'bundle.js',
        },
        resolve: {
            modules: [path.resolve(__dirname, 'src'), 'node_modules'],
            extensions: ['.js', '.jsx'],
        },
        module: {
            rules: [
                {
                    test: /\.(js|jsx)$/,
                    exclude: /node_modules/,
                    loader: 'babel-loader',
                },

                {
                    test: /\.css$/i,
                    use: ['style-loader', 'css-loader'],
                },
                {
                    test: /\.s[ac]ss$/i,
                    use: [
                        'style-loader',
                        'css-loader',
                        'resolve-url-loader',
                        {
                            loader: 'sass-loader',
                            options: {
                                sourceMap: true,
                            },
                        },
                    ],
                },
                {
                    test: /\.(png|jpe?g|gif|svg)$/i,
                    type: 'asset',
                },
            ],
        },
        plugins: [
            new HtmlWebpackPlugin({
                template: './public/index.html',
            }),
            new webpack.HotModuleReplacementPlugin(),
        ],
    };
};
