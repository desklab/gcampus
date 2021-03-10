let path = require('path');

let gulp = require('gulp');
let gulpUtil = require('gulp-util');

let config = require('../config');


let src = config.apps.map(app => path.join(app.src, 'assets/**/*'));
let dest = config.apps.map(app => path.join(app.dest, 'assets'));

gulp.task('assets', () => {
    return gulp.src(src)
        .pipe(gulp.dest(dest))
        .on('error', gulpUtil.log);
});

gulp.task('watch-assets', () => {
    gulp.watch(src, gulp.series('assets'));
});
