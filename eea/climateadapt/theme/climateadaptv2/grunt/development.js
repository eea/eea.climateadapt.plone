module.exports = {
  less: {
    development: {
      options: {
        compress: false,
        sourceMap: true,
        sourceMapFilename: '<%= path.static %>/static/css/source.css.map',
        sourceMapURL: './source.css.map'
      },
      files: {
        // '<%= path.static %>/static/css/main.css': '<%= path.src %>/less/main.less',
        '<%= path.static %>/static/css/compiled-less.css': '<%= path.src %>/less/main.less',
        '<%= path.static %>/static/css/compiled-css.css': '<%= path.src %>/css/*.css',

        // '<%= path.static %>/css/east.css': '<%= path.src %>/less/east.less',
        // '<%= path.static %>/css/south.css': '<%= path.src %>/less/south.less'
      }
    }
  },
  concat: {
    scripts: {
      src: [
        '<%= path.src %>/js/**/*.js'
      ],
      dest: '<%= path.static %>/static/js/main.js'
    },
    // styles: {
    //   src: [
    //     '<%= path.static %>/static/css/compiled-css.css',
    //     '<%= path.static %>/static/css/compiled-less.css'
    //   ],
    //   dest: '<%= path.static %>/static/css/cca.css'
    // }
  },
  // copy: {
  //   scripts: {
  //     files: [
  //       { expand: true,
  //         cwd: '<%= path.src%>/js/',
  //         src: [
  //           'bootstrap.dropdown.js'
  //         ],
  //         dest: '<%= path.static %>/js/'
  //       }
  //     ]
  //   }
  // },
  watch: {
    styles: {
      files: ['<%= path.src %>/less/**/*.less'],
      tasks: ['less:development'],
      options: {
        nospawn: true
      }
    },
    scripts: {
      files: ['<%= path.src %>/js/**/*.js'],
      tasks: ['concat'],
      options: {
        nospawn: true
      }
    },
    templates: {
      files: ['<%= path.static %>/src/tpl/**/*.hbs'],
      tasks: ['template:dev'],
      options: {
        nospawn: true
      }
    }
  }
}
