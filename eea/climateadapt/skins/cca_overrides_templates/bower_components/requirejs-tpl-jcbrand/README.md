# requirejs-underscore-tpl

This is an AMD loader for [Underscore.js micro-templates](http://underscorejs.org/#template).
It's a better maintained fork of [jfparadis/requirejs-tpl](https://github.com/jfparadis/requirejs-tpl)
and can be used as a drop-in replacement to [ZeeAgency/requirejs-tpl](http://github.com/ZeeAgency/requirejs-tpl).

## Overview

- Uses the ``_.template()`` engine provided by Underscore.js.
- Uses the official ``text`` loader plugin provided by Require.js.
- You don't have to specify the template file extension (``.html is assumed``, but this is configurable).

Notes:

- Both libraries can be removed at build-time using ``r.js``.
- The extension ``.html`` is assumed, and this makes loading templates similar to loading JavaScript files with Require.js (all extensions are assumed).

## Installation

To install it via NPM.js:

```
npm install requirejs-undertemplate
```

Then configure require.js:

```
require.config({
  paths: {
    underscore: 'node_modules/underscore/underscore',
    text: 'node_modules/requirejs-text/text'
    tpl: 'node_modules/requirejs-undertemplate/tpl'
  },
  shim: {
    'underscore': {
      exports: '_'
    }
  }
});
```

## Usage

Specify the plugin using ``tpl!`` followed by the template file:

```
require(['backbone', 'tpl!template'], function (Backbone, template) {
  return Backbone.View.extend({
    initialize: function(){
      this.render();
    },
    render: function(){
      this.$el.html(template({message: 'hello'}));
  });
});
```

## Customization

You can specify the template file extension in your main.js:

```
require.config({

  // some paths and shims

  tpl: {
    extension: '.tpl' // default = '.html'
  }
});
```

Underscore allows you to configure the style of templating (more specifically,
the syntax for how variables are interpolated, conditional statements and
comments).  Refer to the [templateSettings](http://underscorejs.org/#template) variable.

Similarly to setting the template file extension, you can set
templateSettings in your main.js:

```
require.config({

    // Use Mustache style syntax for variable interpolation

    templateSettings: {
        evaluate : /\{\[([\s\S]+?)\]\}/g,
        interpolate : /\{\{([\s\S]+?)\}\}/g
    }
});
```

## Optimization

This plugin is compatible with [r.js](http://requirejs.org/docs/optimization.html).

Optimization brings three benefits to a project:

- The templates are bundled within your code and not dynamically loaded which reduces the number of HTTP requests.
- The templates are pre-compiled before being bundled which reduces the work the client has to do.
- You can use the compiled, non-minimized version of the templates to step over the code in a debugger.

The most important build options are:

```
stubModules: ['underscore', 'text', 'tpl']
```

The list of modules to stub out in the optimized file, i.e. the code is replaced with `define('module',{});` by `r.js`

```
removeCombined: true
```

Removes from the output folder the files combined into a build.

## Example

You'll need a web-server to serve the files.
`requirejs-text` is not compatible with the `file://` protocol and thus opening
`index.hml` directly from your browser will not work.


You can use the Node.js-based `http-server` package to serve the example files.

```
  $ npm install
  $ ./node_modules/.bin/http-server
```

Go to [http://localhost:8080/example](http://localhost:8080/example). Your browser should load:

- index.html
- require.js
- main.js
- tpl.js
- underscore.js
- text.js
- message.html

Go to [http://localhost:8080/example-build](http://localhost:8080/example-build). Your browser should load:

- index.html
- require.js
- main.js
