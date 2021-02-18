module.exports = {
  less: {
    production: {
      options: {
        compress: true,
        sourceMap: false,
      },
      files: {
        "<%= path.static %>/css/compiled-less.css":
          "<%= path.src %>/less/main.less",
        "<%= path.static %>css/health.css": "<%= path.src %>/less/health.less",
        "<%= path.static %>css/critical.css":
          "<%= path.src %>/less/critical.less",
        "<%= path.static %>/css/compiled-css.css": "<%= path.src %>/css/*.css",
      },
    },
  },

  concat: {
    scripts: {
      src: ["<%= path.src %>/js/**/*.js"],
      dest: "<%= path.static %>/js/main.js",
    },
  },

  uglify: {
    scripts: {
      files: [
        {
          expand: true,
          cwd: "<%= path.static %>/js",
          src: "**/*.js",
          dest: "<%= path.static %>/js",
        },
      ],
    },
  },

  cachebreaker: {
    dev: {
      options: {
        replacement: "md5",
        match: [
          {
            "health.css": "static/css/health.css",
            "compiled-less.css": "static/css/compiled-less.css",
          },
        ],
      },
      files: {
        src: ["src/tpl/partials/health-head.hbs", "src/tpl/partials/head.hbs"],
      },
    },
  },
};
