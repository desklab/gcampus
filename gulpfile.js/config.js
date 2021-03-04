let path = require('path');


const staticDir = 'static';
const sourceDir = 'static_src';

function App(dir, label) {
    // Base directory of a django app
    this.dir = dir;
    // Label of the django app. Used inside the static files directory
    this.label = label;
    // Static files source directory
    this.src = path.join('.', this.dir, sourceDir);
    // Static files destination directory (compiled/bundled)
    this.dest = path.join('.', this.dir, staticDir, this.label);
}

const apps = [
    new App('gcampus/core', 'gcampuscore'),
];

module.exports = {
    apps: apps,
    staticDir: staticDir,
    sourceDir: sourceDir
}
