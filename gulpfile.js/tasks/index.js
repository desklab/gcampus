let fs = require('fs');

let gulp = require('gulp');
const through = require('through2');
let gulpUtil = require('gulp-util');

let config = require('../config');


let clean = through.obj((chunk, enc, cb) => {
    fs.access(chunk.path, fs.constants.F_OK, (err) => {
        if (!err) {
            // File/directory exists, delete it
            fs.rm(
                chunk.path,
                { recursive: true, force: true },
                err => cb(err, chunk)
            );
        } else {
            // Proceed without raising an exception
            cb(null, chunk);
        }
    })
});

gulp.task('clean', () => {
    return gulp.src(config.apps.map(app => app.dest), {allowEmpty: true})
        .pipe(clean).on('error', gulpUtil.log);
});

gulp.task('build', gulp.series('javascript', 'assets'));
gulp.task('default', gulp.series('clean', 'build'));
