module.exports = {
  less: {
    production: {
      options: {
        compress: true,
        sourceMap: false
      },
      files: {
        '<%= path.static %>/static/css/compiled-less.css': '<%= path.src %>/less/main.less',
        '<%= path.static %>/static/css/compiled-css.css': '<%= path.src %>/css/*.css'
      }
    }
  },
  uglify: {
    scripts: {
      files: [{
        expand: true,
        cwd: '<%= path.static %>/js',
        src: '**/*.js',
        dest: '<%= path.static %>/js'
      }]
    }
  },
  postcss: {
    production: {
      src: '<%= path.static %>/css/*.css',
      options: {
        map: false,
        processors: [
          require('autoprefixer')()
        ]
      }
    }
  }
}
