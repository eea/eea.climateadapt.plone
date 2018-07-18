module.exports = {

  less: {
    production: {
      options: {
        compress: true,
        sourceMap: false
      },
      files: {
        '<%= path.static %>/css/compiled-less.css': '<%= path.src %>/less/main.less',
        '<%= path.static %>/css/compiled-css.css': '<%= path.src %>/css/*.css'
      }
    }
  },

  concat: {
    scripts: {
      src: [
        '<%= path.src %>/js/**/*.js'
      ],
      dest: '<%= path.static %>/js/main.js'
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
  }
};
