var gulp = require('gulp');
var shell = require('gulp-shell');
var clean = require('gulp-clean');
var jslint = require('gulp-jslint');


gulp.task('lint', function() {
  gulp.src('src/**/*.js')
    .pipe(jslint({
      predef: [
        'goog',
        'ol'
      ],
      node: true,
      evil: true,
      nomen: true,
      indent: 2,
      errorsOnly: false
    }));
});

gulp.task('clean', function() {
  gulp.src('node_modules/openlayers/build/info.json', {read: false})
        .pipe(clean());
});

gulp.task('copy', ['clean'], function() {
  gulp.src('webgis.json')
    .pipe(gulp.dest('node_modules/openlayers/build/'));

  gulp.src('webgis-debug.json')
    .pipe(gulp.dest('node_modules/openlayers/build/'));

  gulp.src('src/**/*.js')
    .pipe(gulp.dest('node_modules/openlayers/src/ol/gislab'));

  gulp.src('externs/webgis.js')
    .pipe(gulp.dest('node_modules/openlayers/externs/'));

});

gulp.task('build', ['copy'], // <-- put 'lint' target here, once it's ok
  shell.task(['cd node_modules/openlayers;' +
              'node tasks/build.js build/webgis.json build/ol.min.js'])
);

gulp.task('build-debug', ['copy'],
  shell.task(['cd node_modules/openlayers;' +
              'node tasks/build.js build/webgis-debug.json build/ol.debug.js'])
);

gulp.task('default', ['build', 'build-debug'], function() {

  // copy openlayers
  gulp.src('node_modules/openlayers/build/ol.min.js').
    pipe(gulp.dest('../static/core/lib/'));

  gulp.src('node_modules/openlayers/build/ol.debug.js').
    pipe(gulp.dest('../static/core/lib/'));

  gulp.src('node_modules/openlayers/dist/ol.css').
    pipe(gulp.dest('../static/core/lib/'));

  // copy md5.js
  gulp.src('node_modules/cryptojs/lib/MD5.js').
    pipe(gulp.dest('../static/core/lib/'));

  // copy proj4.js
  gulp.src('node_modules/proj4/dist/proj4.js').
    pipe(gulp.dest('../static/core/lib/'));

});
