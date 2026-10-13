const esbuild = require('esbuild');
const path = require('path');
const fs = require('fs');

const outDir = path.join(__dirname, 'frontend', 'static', 'js', 'bundles');
if (!fs.existsSync(outDir)) {
  fs.mkdirSync(outDir, { recursive: true });
}

async function buildAll() {
  console.log('Building TypeScript, React, and Angular bundles...');

  // 1. React Widgets Bundle
  await esbuild.build({
    entryPoints: [path.join(__dirname, 'frontend', 'src', 'react', 'index.tsx')],
    bundle: true,
    minify: true,
    sourcemap: false,
    format: 'iife',
    target: ['es2020'],
    outfile: path.join(outDir, 'react-widgets.bundle.js'),
    define: {
      'process.env.NODE_ENV': '"production"'
    }
  });
  console.log('✔ React widgets bundle built successfully.');

  // 2. Angular Widgets Bundle
  await esbuild.build({
    entryPoints: [path.join(__dirname, 'frontend', 'src', 'angular', 'main.ts')],
    bundle: true,
    minify: true,
    sourcemap: false,
    format: 'iife',
    target: ['es2020'],
    outfile: path.join(outDir, 'angular-widgets.bundle.js'),
  });
  console.log('✔ Angular widgets bundle built successfully.');
}

buildAll().catch(err => {
  console.error('Build failed:', err);
  process.exit(1);
});
