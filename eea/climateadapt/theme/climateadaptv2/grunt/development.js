module.exports = {
  less: {
    development: {
      options: {
        compress: false,
        sourceMap: true,
        outputSourceFiles: true,
        sourceMapFileInline: true,
        sourceMapRootpath: "../../",
      },
      files: {
        "<%= path.static %>css/compiled-less.css":
          "<%= path.src %>/less/main.less",
        "<%= path.static %>css/critical.css":
          "<%= path.src %>/less/critical.less",
        "<%= path.static %>css/compiled-css.css": "<%= path.src %>/css/*.css",
        "<%= path.static %>css/health.css": "<%= path.src %>/less/health.less",
      },
    },
  },
  copy: {
    scripts: {
      files: [
        {
          expand: true,
          flatten: true,
          src: ["<%= path.src %>/js/*.js"],
          dest: "<%= path.static %>/js/",
        },
      ],
    },
  },
  concat: {
    scripts: {
      src: ["<%= path.src %>/js/**/*.js"],
      dest: "<%= path.static %>/js/main.js",
    },
  },

  watch: {
    styles: {
      files: ["<%= path.src %>/less/**/*.less"],
      tasks: ["less:development"],
      options: {
        nospawn: true,
      },
    },
    scripts: {
      files: ["<%= path.src %>/js/**/*.js"],
      // tasks: ['concat'],
      tasks: ["copy"],
      options: {
        nospawn: true,
      },
    },
    templates: {
      files: ["<%= path.src %>/tpl/**/*.hbs"],
      tasks: ["template:dev"],
      options: {
        nospawn: true,
      },
    },
  },
};
