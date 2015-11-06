/**
 * Gulp build system for GIS.lab web client
 * TODO:
 * 1 - separate to more files
 * 2 - replace jslint with jshint
 * 3 - add fixmyjs
 */

var gulp = require('gulp');
var shell = require('gulp-shell');
var clean = require('gulp-clean');
var jshint = require('gulp-jshint');
var fixmyjs = require('gulp-fixmyjs');
var stylish = require('jshint-stylish');
var ngAnnotate = require('gulp-ng-annotate');
var uglify = require('gulp-uglify');
var concat = require('gulp-concat');
var watch = require('gulp-watch');
var install = require('gulp-install');
var chug = require('gulp-chug');
var minifyCss = require('gulp-minify-css');

var TARGET = '../static/web/';

var CSSS = [
  'node_modules/angular/angular-csp.css',
  'node_modules/angular-material/angular-material.min.css',
  'node_modules/angular-material-data-table/dist/md-data-table.min.css',
  'node_modules/angular-ui-layout/dist/ui-layout.css',
  'node_modules/openlayers/build/ol.min.js',
  'styles/gislab/ui.css'
];

var CORE_WEB_LIBS = [
  'src/core/**/*.module.js',
  'src/web/**/*.module.js',
  'src/core/**/*.js',
  'src/web/**/*.js'
];


var DEPS = [
  'node_modules/angular/angular.min.js',
  'node_modules/angular-animate/angular-animate.min.js',
  'node_modules/angular-aria/angular-aria.min.js',
  'node_modules/angular-material/angular-material.min.js',
  'node_modules/angular-material-data-table/dist/md-data-table.min.js',
  'node_modules/angular-ui-layout/dist/ui-layout.js.min.js'
];

var OL3DEPS = [
  'node_modules/crypto-js/crypto-js.js',
  'node_modules/proj4/dist/proj4.js',
  'node_modules/openlayers/build/ol.min.js'
];

/**
 * Run streaming-integration. Every file you save fill be compiled immedietly
 * NOTE: linter is commented out
 */
gulp.task('stream', ['uglify', 'lint'], function() {

  gulp.watch(CORE_WEB_LIBS, ['lint', 'uglify']);

});


/**
 * compile all source code to one file
 */
gulp.task('uglify', function() {

  gulp.src(CORE_WEB_LIBS)
    .pipe(ngAnnotate({ add: true }))
    .pipe(uglify())
    .pipe(concat('app.min.js'))
    .pipe(gulp.dest(TARGET + 'js/'));

});

/**
 * Minify all css files
 */
gulp.task('csss', function() {
  gulp.src(CSSS)
    .pipe(minifyCss())
    .pipe(concat('styles.min.css'))
    .pipe(gulp.dest(TARGET + 'styles'));

  gulp.src('styles/gislab/icons.svg')
    .pipe(gulp.dest(TARGET + 'styles'));
});


/**
 * Compile OpenLayers with custom code
 */
gulp.task('deps', ['buildol3', 'buildol3-debug'], function() {

  // copy DEPS
  gulp.src(DEPS)
  .pipe(concat('deps.min.js'))
  .pipe(gulp.dest(TARGET + 'js/'));

  // copy openlayers
  gulp.src(OL3DEPS)
  .pipe(uglify())
  .pipe(concat('ol3-deps.min.js'))
  .pipe(gulp.dest(TARGET + 'js/'));


});


///**
// * Fix javascript style
// * this really needs to be fixed!
// */
//gulp.task('fixstyle', function() {
//  gulp.src('src/**/*.js')
//    .pipe(fixmyjs({ }))
//    .pipe(gulp.dest('src'));
//});


/**
 * JavaScript linter
 */
gulp.task('lint', function() {

  gulp.src('src/**/*.js')
    .pipe(jshint({
    }))
    .pipe(jshint.reporter(stylish));
});


/**
 * clena info.son
 */
gulp.task('cleanol3', function() {
  gulp.src('node_modules/openlayers/build/info.json', {read: false})
        .pipe(clean());
});


/**
 * copy our source files to openlayer3
 */
gulp.task('copyol3-src', ['cleanol3'], function() {
  gulp.src('webgis.json')
    .pipe(gulp.dest('node_modules/openlayers/build/'));

  gulp.src('webgis-debug.json')
    .pipe(gulp.dest('node_modules/openlayers/build/'));

  gulp.src('src/ol3/**/*.js')
    .pipe(gulp.dest('node_modules/openlayers/src/ol/gislab'));

  gulp.src('externs/webgis.js')
    .pipe(gulp.dest('node_modules/openlayers/externs/'));

});


/**
 * build ol3 app
 */
gulp.task('buildol3', ['copyol3-src'],
  shell.task(['cd node_modules/openlayers;' +
              'node tasks/build.js build/webgis.json build/ol.min.js'])
);


/**
 * build ol3 in debug mode
 */
gulp.task('buildol3-debug', ['copyol3-src'],
  shell.task(['cd node_modules/openlayers;' +
              'node tasks/build.js build/webgis-debug.json build/ol.debug.js'])
);


/**
 * default task
 * build deps, minify css, uglify
 */
gulp.task('default', ['deps', 'csss', 'uglify'], function() {

});
