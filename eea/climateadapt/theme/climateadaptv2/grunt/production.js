module.exports = {
  less: {
    production: {
      options: {
        compress: true,
        sourceMap: false
      },
      files: {
        '<%= path.static %>/css/main.css': '<%= path.src %>/less/main.less',
        '<%= path.static %>/css/east.css': '<%= path.src %>/less/east.less',
        '<%= path.static %>/css/south.css': '<%= path.src %>/less/south.less'
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
