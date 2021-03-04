let path = require('path');

let gulp = require('gulp');
let gulpUtil = require('gulp-util');
let sourcemaps = require('gulp-sourcemaps');
let babel = require('gulp-babel');

let config = require('../config');


let src = config.apps.map(app => path.join(app.src, 'js/**/*.js'));
let dest = config.apps.map(app => path.join(app.dest, 'js'));

gulp.task('javascript', () => {
    return gulp.src(src)
        .pipe(sourcemaps.init())
        .pipe(babel({
            presets: ['@babel/preset-env']
        }))
        .pipe(sourcemaps.write(dest))
        .pipe(gulp.dest(dest))
        .on('error', gulpUtil.log);
});
