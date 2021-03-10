let path = require('path');

let gulp = require('gulp');
let gulpUtil = require('gulp-util');
let gulpIf = require('gulp-if');
const gulpEsbuild = require('gulp-esbuild')

let config = require('../config');


let src = config.apps.map(app => path.join(app.src, 'js/**/*.js'));
let dest = config.apps.map(app => path.join(app.dest, 'js'));

gulp.task('javascript', () => {
    return gulp.src(src)
        .pipe(gulpEsbuild({
            bundle: true,
            sourcemap: config.sourceMaps,
            format: "iife"
        }))
        .pipe(gulp.dest(dest))
        .on('error', gulpUtil.log);
});

gulp.task('watch-javascript', () => {
    gulp.watch(src, gulp.series('javascript'));
});
