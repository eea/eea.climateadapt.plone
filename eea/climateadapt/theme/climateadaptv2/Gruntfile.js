module.exports = function (grunt) {
  require("load-grunt-tasks")(grunt);

  grunt.loadNpmTasks("grunt-template-html");

  // Config
  var merge = require("merge"),
    config = {};

  config.path = {
    static: "./static/",
    src: "src",
    node: "node_modules",
  };

  [
    require("./grunt/base.js"),
    require("./grunt/development.js"),
    require("./grunt/production.js"),
  ].forEach(function (settings) {
    config = merge.recursive(true, config, settings);
  });

  grunt.initConfig(config);

  // Tasks
  grunt.registerTask("development", [
    "template:dev",
    "less:development",
    // 'concat',
    "copy",
  ]);

  grunt.registerTask("production", [
    "template:dev",
    "less:production",
    // 'concat',
    "copy",
    "uglify",
  ]);

  grunt.registerTask("default", [
    "development",
    //'watch'
  ]);
};
