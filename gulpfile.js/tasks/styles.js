let path = require('path');

var Fiber = require('fibers');
let gulp = require('gulp');
let gulpUtil = require('gulp-util');
let gulpIf = require('gulp-if');
let sourcemaps = require('gulp-sourcemaps');
let sass = require('gulp-sass');
let postcss = require('gulp-postcss');
let autoprefixer = require('autoprefixer');
let cssnano = require('cssnano');

let config = require('../config');


sass.compiler = require('sass');
let src = config.apps.map(app => path.join(app.src, 'styles/**/*.scss'));
let dest = config.apps.map(app => path.join(app.dest, 'styles'));

gulp.task('styles', function () {
    return gulp.src(src)
        .pipe(gulpIf(config.sourceMaps, sourcemaps.init()))
        .pipe(sass({fiber: Fiber, includePaths: ['node_modules']}).on('error', sass.logError))
        .pipe(postcss([
            autoprefixer({cascade: false}),
            cssnano({discardUnused: {fontFace: false}})
        ]))
        .pipe(gulpIf(config.sourceMaps, sourcemaps.write()))
        .pipe(gulp.dest(dest))
        .on('error', gulpUtil.log);
});
