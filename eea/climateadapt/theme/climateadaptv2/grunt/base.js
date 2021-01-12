module.exports = {
  template: {
    dev: {
      engine: "handlebars",
      cwd: "src/tpl/",
      partials: ["src/tpl/partials/*.hbs"],
      // data: 'src/tpl/helpers.json',
      options: {
        //  you can reference in template {{ themeurl }}
        helpers: {
          themeurl: "/cca/++theme++climateadaptv2/",
        },
      },
      files: [
        {
          expand: true, // Enable dynamic expansion.
          cwd: "src/tpl/", // Src matches are relative to this path.
          src: "*.hbs", // Actual pattern(s) to match.
          dest: "./", // Destination path prefix.
          ext: ".html", // Dest filepaths will have this extension.
        },
      ],
    },
  },
};
