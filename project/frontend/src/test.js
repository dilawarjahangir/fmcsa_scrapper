const fs = require('fs');
const path = require('path');

// Determine the base directory (the directory where this script resides)
const BASE_DIR = __dirname;
const OUTPUT_FILENAME = 'allcode.js';
const outputFilePath = path.join(BASE_DIR, OUTPUT_FILENAME);

/**
 * Recursively reads a directory and appends the contents of each .js and .jsx file to the output file.
 *
 * @param {string} dirPath - The directory to read from.
 */
function gatherJsFiles(dirPath) {
  // Read all items in the directory
  const items = fs.readdirSync(dirPath);
  items.forEach(item => {
    const fullPath = path.join(dirPath, item);
    const stats = fs.statSync(fullPath);
    
    if (stats.isDirectory()) {
      // Recursively process subdirectories
      gatherJsFiles(fullPath);
    } else if ((item.endsWith('.js') || item.endsWith('.jsx')) && item !== OUTPUT_FILENAME) {
      // Get the file path relative to BASE_DIR for commenting
      const relativePath = path.relative(BASE_DIR, fullPath);
      fs.appendFileSync(outputFilePath, `\n// ${relativePath}:\n\n`);
      // Read and append the file's contents
      const content = fs.readFileSync(fullPath, 'utf8');
      fs.appendFileSync(outputFilePath, content);
      fs.appendFileSync(outputFilePath, "\n");
    }
  });
}

function main() {
  // If 'allcode.js' exists, remove it to start fresh
  if (fs.existsSync(outputFilePath)) {
    fs.unlinkSync(outputFilePath);
  }
  
  // Gather all .js and .jsx files from BASE_DIR
  gatherJsFiles(BASE_DIR);
  console.log(`All .js and .jsx files have been combined into "${OUTPUT_FILENAME}"`);
}

main();
